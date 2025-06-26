import json
import shutil
from pathlib import Path
from typing import Any, Dict, List
from ..utils.logger import log_info, log_error, log_warning
from ..utils.cli_utils import show_success_message, show_error_message, show_warning_message
from ..models.config import Config
from ..models.data import DataRow

# TODO: Make this configurable via CLI/config
DEFAULT_TEMPLATE_NAME = "Example_PBIP"

class PBIPProcessor:
    """Process PBIP templates to generate new projects."""
    
    def __init__(self, config: Config, template_name: str = DEFAULT_TEMPLATE_NAME):
        self.config = config
        self.template_name = template_name
    
    def process_data(self, template_path: Path, data: List[DataRow], output_dir: Path) -> int:
        """Process all data rows and generate PBIP projects."""
        success_count = 0
        
        for i, row in enumerate(data, 1):
            try:
                log_info(f"Processing row {i}/{len(data)}: {row.get_folder_name()}")
                
                if self.process_row(template_path, row, output_dir):
                    success_count += 1
                    log_info(f"Generated PBIP folder: {row.get_folder_name()}")
                else:
                    show_error_message(f"Failed to process row {i}: Failed to generate PBIP")
                    
            except (OSError, ValueError) as e:
                show_error_message(f"Failed to process row {i}: {str(e)}")
            except Exception as e:
                show_error_message(f"Unexpected error in row {i}: {str(e)}")
                raise
        
        return success_count
    
    def process_row(self, template_path: Path, row: DataRow, output_dir: Path) -> bool:
        """Process a single data row and generate a PBIP project."""
        try:
            # Create output folder name
            folder_name = row.get_folder_name()
            output_folder = output_dir / folder_name
            report_name = row.data.get("Report_Name", folder_name)
            
            # Copy the entire template folder
            if not self._copy_pbip_folder(template_path, output_folder):
                return False
            
            # Rename internal files and folders
            self._rename_internal_files_and_folders(output_folder, report_name)
            
            # Recursively replace all Example_PBIP references in all files
            self._replace_references_in_files(output_folder, self.template_name, report_name)
            
            # Update parameters in model.bim
            semantic_model_folder = output_folder / f"{report_name}.SemanticModel"
            model_bim_path = semantic_model_folder / "model.bim"
            
            if not self._update_parameters_in_model_bim(model_bim_path, row):
                show_error_message("Failed to update parameters in model.bim")
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
    
    def _update_parameters_in_model_bim(self, model_bim_path: Path, row: DataRow) -> bool:
        """Update parameter values in the model.bim file."""
        try:
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
        """Rename all internal files/folders and references from Example_PBIP to report_name."""
        try:
            # Rename .pbip file
            old_pbip = output_folder / f"{self.template_name}.pbip"
            new_pbip = output_folder / f"{report_name}.pbip"
            if old_pbip.exists():
                old_pbip.rename(new_pbip)
            
            # Rename .Report folder
            old_report = output_folder / f"{self.template_name}.Report"
            new_report = output_folder / f"{report_name}.Report"
            if old_report.exists():
                old_report.rename(new_report)
            
            # Rename .SemanticModel folder
            old_semantic = output_folder / f"{self.template_name}.SemanticModel"
            new_semantic = output_folder / f"{report_name}.SemanticModel"
            if old_semantic.exists():
                old_semantic.rename(new_semantic)
            
            # Update references in the .pbip file
            if new_pbip.exists():
                with open(new_pbip, 'r', encoding='utf-8') as f:
                    pbip_data = f.read()
                pbip_data = pbip_data.replace(self.template_name, report_name)
                with open(new_pbip, 'w', encoding='utf-8') as f:
                    f.write(pbip_data)
        except (OSError, ValueError) as e:
            show_error_message(f"Failed to rename internal files/folders: {str(e)}")
        except Exception as e:
            show_error_message(f"Unexpected error renaming files/folders: {str(e)}")
            raise

    def _replace_references_in_files(self, folder: Path, old: str, new: str):
        """Recursively replace all occurrences of old with new in all text files in the folder."""
        for path in folder.rglob('*'):
            if path.is_file():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if old in content:
                        new_content = content.replace(old, new)
                        if new_content != content:
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                except (OSError, UnicodeDecodeError) as e:
                    show_warning_message(f"Failed to update references in {path}: {str(e)}")
                except Exception as e:
                    show_warning_message(f"Unexpected error updating references in {path}: {str(e)}")
                    raise 