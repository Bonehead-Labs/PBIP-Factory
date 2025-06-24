import json
import shutil
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

from ..models.config import AppConfig, ParameterConfig
from ..utils.file_utils import read_json, write_json
from ..utils.logger import log_info, log_error

class PBIPProcessor:
    def __init__(self, template_path: Path, config: dict, output_dir: Path):
        self.template_path = template_path
        self.config = AppConfig(**config)
        self.output_dir = output_dir
        self._validate_template()

    def _validate_template(self):
        """Validate that the template path is a valid PBIP folder."""
        if not self.template_path.is_dir():
            raise ValueError(f"Template path must be a directory: {self.template_path}")
        
        # Check for required PBIP files
        pbip_file = self.template_path / f"{self.template_path.name}.pbip"
        if not pbip_file.exists():
            raise ValueError(f"PBIP file not found: {pbip_file}")
        
        # Check for Report and SemanticModel folders
        report_folder = self.template_path / f"{self.template_path.name}.Report"
        semantic_model_folder = self.template_path / f"{self.template_path.name}.SemanticModel"
        
        if not report_folder.exists():
            raise ValueError(f"Report folder not found: {report_folder}")
        
        if not semantic_model_folder.exists():
            raise ValueError(f"SemanticModel folder not found: {semantic_model_folder}")
        
        # Check for model.bim file
        model_bim = semantic_model_folder / "model.bim"
        if not model_bim.exists():
            raise ValueError(f"model.bim file not found: {model_bim}")
        
        log_info(f"Validated PBIP template: {self.template_path}")

    def _update_parameter_in_model_bim(self, model_bim_path: Path, param_name: str, new_value: Any) -> bool:
        """Update a parameter value in model.bim file."""
        try:
            # Read the model.bim file
            with open(model_bim_path, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            
            # Find the parameter in expressions
            expressions = model_data.get("model", {}).get("expressions", [])
            parameter_found = False
            
            for expression in expressions:
                if expression.get("name") == param_name:
                    # Update the expression value
                    # The expression format is: "\"value\" meta [IsParameterQuery=true, Type=\"Any\", IsParameterQueryRequired=true]"
                    if isinstance(new_value, str):
                        # Escape quotes in string values
                        escaped_value = new_value.replace('"', '\\"')
                        expression["expression"] = f'"{escaped_value}" meta [IsParameterQuery=true, Type="Any", IsParameterQueryRequired=true]'
                    else:
                        # For non-string values, convert to string
                        expression["expression"] = f'"{str(new_value)}" meta [IsParameterQuery=true, Type="Any", IsParameterQueryRequired=true]'
                    
                    parameter_found = True
                    log_info(f"Updated parameter '{param_name}' to '{new_value}'")
                    break
            
            if not parameter_found:
                log_error(f"Parameter '{param_name}' not found in model.bim")
                return False
            
            # Write the updated model.bim file
            with open(model_bim_path, 'w', encoding='utf-8') as f:
                json.dump(model_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            log_error(f"Failed to update parameter '{param_name}' in model.bim: {e}")
            return False

    def _copy_pbip_folder(self, source_path: Path, dest_path: Path) -> bool:
        """Copy the entire PBIP folder to a new location."""
        try:
            if dest_path.exists():
                shutil.rmtree(dest_path)
            
            shutil.copytree(source_path, dest_path)
            log_info(f"Copied PBIP folder to: {dest_path}")
            return True
            
        except Exception as e:
            log_error(f"Failed to copy PBIP folder: {e}")
            return False

    def _generate_folder_name(self, row: Dict[str, Any]) -> str:
        """Generate folder name based on naming pattern and row data."""
        try:
            pattern = self.config.output.naming_pattern
            folder_name = pattern.format(**row)
            
            # Clean folder name (remove invalid characters)
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                folder_name = folder_name.replace(char, '_')
            
            # Add timestamp if needed
            if '{timestamp}' in folder_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                folder_name = folder_name.replace('{timestamp}', timestamp)
            
            return folder_name
            
        except Exception as e:
            log_error(f"Failed to generate folder name: {e}")
            # Fallback to timestamp-based folder name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"pbip_{timestamp}"

    def process_row(self, row: Dict[str, Any]) -> Path:
        """Process a single row and generate a new PBIP folder."""
        try:
            # Generate folder name
            folder_name = self._generate_folder_name(row)
            output_folder = self.output_dir / folder_name
            
            # Copy the PBIP folder
            if not self._copy_pbip_folder(self.template_path, output_folder):
                raise Exception("Failed to copy PBIP folder")
            
            # Update parameters in model.bim
            semantic_model_folder = output_folder / f"{self.template_path.name}.SemanticModel"
            model_bim_path = semantic_model_folder / "model.bim"
            
            for param in self.config.parameters:
                if param.name in row:
                    value = row[param.name]
                    
                    # Type conversion if needed
                    if param.type == "integer":
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            log_error(f"Failed to convert {param.name} to integer: {value}")
                            continue
                    elif param.type == "float":
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            log_error(f"Failed to convert {param.name} to float: {value}")
                            continue
                    elif param.type == "boolean":
                        if isinstance(value, str):
                            value = value.lower() in ('true', '1', 'yes', 'on')
                    
                    # Update the parameter in model.bim
                    if not self._update_parameter_in_model_bim(model_bim_path, param.name, value):
                        log_error(f"Failed to update parameter {param.name}")
            
            log_info(f"Generated PBIP folder: {folder_name}")
            return output_folder
            
        except Exception as e:
            log_error(f"Failed to process row: {e}")
            raise

    def process_all(self, data: List[Dict[str, Any]]) -> List[Path]:
        """Process all rows from the CSV and generate PBIP folders."""
        generated_folders = []
        
        for i, row in enumerate(data, 1):
            try:
                output_folder = self.process_row(row)
                generated_folders.append(output_folder)
                log_info(f"Processed row {i}/{len(data)}: {output_folder.name}")
            except Exception as e:
                log_error(f"Failed to process row {i}: {e}")
                continue
        
        return generated_folders

    def validate_parameters(self, row: Dict[str, Any]) -> List[str]:
        """Validate that all required parameters are present in the row."""
        missing_params = []
        
        for param in self.config.parameters:
            if param.name not in row:
                missing_params.append(param.name)
        
        return missing_params

    def get_parameter_summary(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of parameter changes for a row."""
        summary = {}
        
        for param in self.config.parameters:
            if param.name in row:
                summary[param.name] = {
                    'type': param.type,
                    'value': row[param.name]
                }
        
        return summary 