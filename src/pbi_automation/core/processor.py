import json
import shutil
from pathlib import Path
from typing import Any, Dict, List
from ..utils.logger import log_info, log_error, log_warning
from ..utils.cli_utils import show_success_message, show_error_message, show_warning_message, show_info_message
from ..utils.tmdl_parser import TMDLParser
from ..models.config import Config
from ..models.data import DataRow

DEFAULT_TEMPLATE_NAME = "Example_PBIP"

class PBIPProcessor:
    """Process PBIP templates to generate new projects."""
    
    def __init__(self, config: Config, template_name: str = DEFAULT_TEMPLATE_NAME):
        self.config = config
        self.template_name = template_name
        self.tmdl_parser = TMDLParser()
    
    def process_data(self, template_path: Path, data: List[DataRow], output_dir: Path) -> int:
        """Process all CSV rows and generate PBIP projects.

        Returns the number of successfully generated projects.
        """
        num_successful_projects = 0
        total_rows = len(data)

        for row_index, data_row in enumerate(data, start=1):
            try:
                log_info(f"Processing row {row_index}/{total_rows}: {data_row.get_folder_name()}")

                if self.process_row(template_path, data_row, output_dir):
                    num_successful_projects += 1
                    log_info(f"Generated PBIP folder: {data_row.get_folder_name()}")
                else:
                    show_error_message(f"Failed to process row {row_index}: Failed to generate PBIP")

            except (OSError, ValueError) as error:
                show_error_message(f"Failed to process row {row_index}: {str(error)}")
            except Exception as unexpected_error:
                show_error_message(f"Unexpected error in row {row_index}: {str(unexpected_error)}")
                raise

        return num_successful_projects
    
    def process_row(self, template_path: Path, row: DataRow, output_dir: Path) -> bool:
        """Process a single CSV record and generate a PBIP project.

        Steps:
        1) Copy template → output folder
        2) Rename artifacts (.pbip, .Report, .SemanticModel) and internal references
        3) Update parameter values in BIM/TMDL model files
        4) Remove cache for clean refresh in Power BI Desktop
        """
        try:
            # Create output folder name
            folder_name = row.get_folder_name()
            output_folder = output_dir / folder_name
            report_name = row.data.get("Report_Name", folder_name)
            
            # Copy the entire template folder
            if not self._copy_pbip_folder(template_path, output_folder):
                return False
            
            # Rename internal files and folders to match the new report name
            self._rename_internal_files_and_folders(output_folder, report_name)
            
            # Get the actual template name for reference replacement
            template_name = None
            for item in output_folder.iterdir():
                if item.is_dir() and item.name.endswith('.Report'):
                    template_name = item.name[:-7]  # Remove '.Report' suffix
                    break
                elif item.is_file() and item.name.endswith('.pbip'):
                    template_name = item.name[:-5]  # Remove '.pbip' suffix
                    break
            
            if template_name:
                # Recursively replace all template-name references across text files
                self._replace_references_in_files(output_folder, template_name, report_name)
            
            # Update parameters based on detected semantic model format (BIM or TMDL)
            semantic_model_folder = output_folder / f"{report_name}.SemanticModel"
            model_format = self.tmdl_parser.detect_model_format(semantic_model_folder)
            
            if model_format == "bim":
                if not self._update_parameters_in_model_bim(semantic_model_folder, row):
                    show_error_message("Failed to update parameters in model.bim")
                    return False
            elif model_format == "tmdl":
                if not self._update_parameters_in_tmdl(semantic_model_folder, row):
                    show_error_message("Failed to update parameters in TMDL files")
                    return False
            else:
                show_error_message(f"Unsupported model format: {model_format}")
                return False
            
            # Delete cache.abf file for proper data loading
            if not self._delete_cache_file(semantic_model_folder):
                show_warning_message("Failed to delete cache.abf file")
            
            return True
            
        except (OSError, ValueError) as e:
            show_error_message(f"Failed to process row: {str(e)}")
            return False
        except Exception as e:
            show_error_message(f"Unexpected error in process_row: {str(e)}")
            raise
    
    def _copy_pbip_folder(self, source_path: Path, dest_path: Path) -> bool:
        """Copy the entire PBIP folder to a new location."""
        try:
            if dest_path.exists():
                shutil.rmtree(dest_path)
            
            # Copy the entire folder structure as-is
            shutil.copytree(source_path, dest_path)
            log_info(f"Copied PBIP folder to: {dest_path}")
            return True
            
        except (OSError, shutil.Error) as e:
            show_error_message(f"Failed to copy PBIP folder: {str(e)}")
            return False
        except Exception as e:
            show_error_message(f"Unexpected error copying PBIP folder: {str(e)}")
            raise
    
    def _update_parameters_in_model_bim(self, semantic_model_folder: Path, row: DataRow) -> bool:
        """Update parameter values in the model.bim file."""
        try:
            model_bim_path = semantic_model_folder / "model.bim"
            
            # Read the model.bim file
            with open(model_bim_path, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            
            # Update each parameter - expressions are under model.expressions
            model = model_data.get("model", {})
            expressions = model.get("expressions", [])
            updated = False
            
            for expression in expressions:
                param_name = expression.get("name")
                
                if param_name in row.data:
                    new_value = row.data[param_name]
                    old_expression = expression.get("expression", "")
                    
                    # Update the expression with the new value
                    # Format: "value" meta [IsParameterQuery=true, Type="Any", IsParameterQueryRequired=true]
                    new_expression = f'"{new_value}" meta [IsParameterQuery=true, Type="Any", IsParameterQueryRequired=true]'
                    expression["expression"] = new_expression
                    
                    show_success_message(f"Updated parameter '{param_name}' to '{new_value}'")
                    updated = True
            
            if not updated:
                show_warning_message("No parameters were updated")
                return True
            
            # Write the updated model.bim file
            with open(model_bim_path, 'w', encoding='utf-8') as f:
                json.dump(model_data, f, indent=2)
            
            return True
            
        except (OSError, json.JSONDecodeError) as e:
            show_error_message(f"Failed to update parameters in model.bim: {str(e)}")
            return False
        except Exception as e:
            show_error_message(f"Unexpected error updating model.bim: {str(e)}")
            raise
    
    def _update_parameters_in_tmdl(self, semantic_model_folder: Path, row: DataRow) -> bool:
        """Update parameter values in all .tmdl files by replacing old values with new ones everywhere they appear."""
        try:
            # Get all .tmdl files in the semantic model folder
            tmdl_files = list(semantic_model_folder.rglob('*.tmdl'))
            if not tmdl_files:
                show_warning_message("No .tmdl files found in semantic model folder")
                return True

            # For each parameter in the row, update all instances of its value in all TMDL files
            updated_any = False
            for param_name, new_value in row.data.items():
                # First, we need to find the current value of this parameter
                # Look for the parameter definition in TMDL files
                current_value = None
                for tmdl_file in tmdl_files:
                    try:
                        with open(tmdl_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Look for parameter definition: table ParamName ... source = "value" meta [IsParameterQuery=true, ...]
                        import re
                        table_pattern = rf'table\s+{re.escape(param_name)}\s*\n.*?source\s*=\s*"([^"]+)"\s*meta\s*\[IsParameterQuery=true'
                        match = re.search(table_pattern, content, re.DOTALL | re.MULTILINE)
                        
                        if match:
                            current_value = match.group(1)
                            break
                    except Exception:
                        continue
                
                if current_value is None:
                    show_warning_message(f"Could not find current value for parameter '{param_name}'")
                    continue
                
                if current_value == new_value:
                    show_info_message(f"Parameter '{param_name}' already has value '{new_value}'")
                    continue
                
                # Now update all instances of the current value to the new value in all TMDL files
                for tmdl_file in tmdl_files:
                    try:
                        with open(tmdl_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Replace all instances of the old value with the new value
                        if current_value in content:
                            new_content = content.replace(current_value, new_value)
                            if new_content != content:
                                with open(tmdl_file, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                updated_any = True
                                show_success_message(f"Updated parameter '{param_name}' from '{current_value}' to '{new_value}' in {tmdl_file.name}")
                                
                    except Exception as e:
                        show_warning_message(f"Failed to update {param_name} in {tmdl_file}: {str(e)}")
                        continue
                        
            if updated_any:
                show_success_message("Updated parameter values in TMDL files")
            else:
                show_warning_message("No parameter values were updated in TMDL files")
            return True
        except Exception as e:
            show_error_message(f"Unexpected error updating TMDL parameters: {str(e)}")
            raise
    
    def _delete_cache_file(self, semantic_model_folder: Path) -> bool:
        """Delete the cache.abf file from the .pbi folder within the semantic model."""
        try:
            pbi_folder = semantic_model_folder / ".pbi"
            cache_file = pbi_folder / "cache.abf"
            
            if cache_file.exists():
                cache_file.unlink()
                log_info(f"Deleted cache.abf file: {cache_file}")
                return True
            else:
                show_warning_message(f"cache.abf file not found: {cache_file}")
                return True
            
        except OSError as e:
            show_error_message(f"Failed to delete cache.abf file: {str(e)}")
            return False
        except Exception as e:
            show_error_message(f"Unexpected error deleting cache.abf file: {str(e)}")
            raise
    
    def _rename_internal_files_and_folders(self, output_folder: Path, report_name: str):
        """Rename all internal files/folders and references from template name to report_name, and update .pbip and .platform files accordingly."""
        try:
            # Get the actual template name from the folder structure
            template_name = None
            for item in output_folder.iterdir():
                if item.is_dir() and item.name.endswith('.Report'):
                    template_name = item.name[:-7]  # Remove '.Report' suffix
                    break
                elif item.is_file() and item.name.endswith('.pbip'):
                    template_name = item.name[:-5]  # Remove '.pbip' suffix
                    break
            if not template_name:
                show_error_message("Could not determine template name from folder structure")
                return
            # Rename .pbip file
            old_pbip = output_folder / f"{template_name}.pbip"
            new_pbip = output_folder / f"{report_name}.pbip"
            if old_pbip.exists():
                old_pbip.rename(new_pbip)
            # Rename .Report folder
            old_report = output_folder / f"{template_name}.Report"
            new_report = output_folder / f"{report_name}.Report"
            if old_report.exists():
                old_report.rename(new_report)
            # Rename .SemanticModel folder
            old_semantic = output_folder / f"{template_name}.SemanticModel"
            new_semantic = output_folder / f"{report_name}.SemanticModel"
            if old_semantic.exists():
                old_semantic.rename(new_semantic)
            # Update references in all files and folders (including .platform)
            self._replace_references_in_files(output_folder, template_name, report_name)
            # Update .pbip file: only keep the report artifact
            if new_pbip.exists():
                with open(new_pbip, 'r', encoding='utf-8') as f:
                    pbip_data = json.load(f)
                # Replace template name with report name in all paths
                pbip_data_str = json.dumps(pbip_data, indent=2)
                pbip_data_str = pbip_data_str.replace(template_name, report_name)
                pbip_data = json.loads(pbip_data_str)
                # Only keep the report artifact
                artifacts = pbip_data.get("artifacts", [])
                artifacts = [artifact for artifact in artifacts if "report" in artifact]
                pbip_data["artifacts"] = artifacts
                with open(new_pbip, 'w', encoding='utf-8') as f:
                    json.dump(pbip_data, f, indent=2)
        except (OSError, ValueError, json.JSONDecodeError) as e:
            show_error_message(f"Failed to rename internal files/folders: {str(e)}")
        except Exception as e:
            show_error_message(f"Unexpected error renaming files/folders: {str(e)}")
            raise

    def _replace_references_in_files(self, folder: Path, old: str, new: str):
        """Recursively replace all occurrences of old with new in all text files in the folder."""
        # Define binary file extensions to skip
        binary_extensions = {'.abf', '.bin', '.exe', '.dll', '.so', '.dylib', '.pyd', '.pyc', '.pyo'}
        
        for path in folder.rglob('*'):
            if path.is_file():
                # Skip binary files
                if path.suffix.lower() in binary_extensions:
                    continue
                    
                try:
                    # Try to read as text first
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Special handling for .platform files
                    if path.name == '.platform':
                        try:
                            platform_data = json.loads(content)
                            if 'metadata' in platform_data and 'displayName' in platform_data['metadata']:
                                # Replace the entire displayName with the new report name
                                platform_data['metadata']['displayName'] = new
                                new_content = json.dumps(platform_data, indent=2)
                                if new_content != content:
                                    with open(path, 'w', encoding='utf-8') as f:
                                        f.write(new_content)
                        except json.JSONDecodeError:
                            # If it's not valid JSON, treat as regular text file
                            if old in content:
                                new_content = content.replace(old, new)
                                if new_content != content:
                                    with open(path, 'w', encoding='utf-8') as f:
                                        f.write(new_content)
                    else:
                        # Regular text file replacement
                        if old in content:
                            new_content = content.replace(old, new)
                            if new_content != content:
                                with open(path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                except (OSError, UnicodeDecodeError) as e:
                    # Skip files that can't be read as text (likely binary)
                    continue
                except Exception as e:
                    show_warning_message(f"Unexpected error updating references in {path}: {str(e)}")
                    raise 