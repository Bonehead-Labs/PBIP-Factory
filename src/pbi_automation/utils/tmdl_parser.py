"""
TMDL (Tabular Model Definition Language) parser and manipulator.

This module provides functionality to parse TMDL files, detect parameters,
and update parameter values in TMDL format.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ..utils.logger import log_info, log_error, log_warning


class TMDLParser:
    """Parser for TMDL (Tabular Model Definition Language) files."""
    
    def __init__(self):
        self.parameter_pattern = re.compile(
            r'source\s*=\s*"([^"]+)"\s*meta\s*\[IsParameterQuery=true[^\]]*\]',
            re.MULTILINE | re.DOTALL
        )
        self.table_name_pattern = re.compile(r'^table\s+(\w+)', re.MULTILINE)
        self.partition_pattern = re.compile(
            r'partition\s+(\w+)\s*=\s*m\s*\n(.*?)(?=\n\w|\n$|\Z)',
            re.MULTILINE | re.DOTALL
        )
    
    def detect_model_format(self, semantic_model_path: Path) -> str:
        """
        Detect whether the semantic model uses BIM or TMDL format.
        
        Args:
            semantic_model_path: Path to the semantic model folder
            
        Returns:
            'bim' or 'tmdl'
        """
        # Check for model.bim file
        model_bim = semantic_model_path / "model.bim"
        if model_bim.exists():
            return "bim"
        
        # Check for TMDL structure
        definition_folder = semantic_model_path / "definition"
        model_tmdl = definition_folder / "model.tmdl"
        if definition_folder.exists() and model_tmdl.exists():
            return "tmdl"
        
        return "unknown"
    
    def find_parameter_tables(self, semantic_model_path: Path) -> List[str]:
        """
        Find all table files that contain parameters in TMDL format.
        
        Args:
            semantic_model_path: Path to the semantic model folder
            
        Returns:
            List of table names that contain parameters
        """
        parameter_tables = []
        definition_folder = semantic_model_path / "definition"
        tables_folder = definition_folder / "tables"
        
        if not tables_folder.exists():
            log_warning(f"Tables folder not found: {tables_folder}")
            return parameter_tables
        
        for table_file in tables_folder.glob("*.tmdl"):
            try:
                with open(table_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if this table contains parameters
                if self.parameter_pattern.search(content):
                    table_name = table_file.stem
                    parameter_tables.append(table_name)
                    log_info(f"Found parameter table: {table_name}")
                    
            except (OSError, UnicodeDecodeError) as e:
                log_error(f"Failed to read table file {table_file}: {str(e)}")
            except Exception as e:
                log_error(f"Unexpected error reading table file {table_file}: {str(e)}")
        
        return parameter_tables
    
    def extract_parameters_from_table(self, table_file_path: Path) -> Dict[str, str]:
        """
        Extract parameter names and their current values from a TMDL table file.
        
        Args:
            table_file_path: Path to the TMDL table file
            
        Returns:
            Dictionary mapping parameter names to their current values
        """
        parameters = {}
        
        try:
            with open(table_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all parameter expressions
            matches = self.parameter_pattern.finditer(content)
            
            for match in matches:
                # Extract the parameter value from the source expression
                param_value = match.group(1)
                
                # Get the table name (which is the parameter name)
                table_name_match = self.table_name_pattern.search(content)
                if table_name_match:
                    param_name = table_name_match.group(1)
                    parameters[param_name] = param_value
                    log_info(f"Extracted parameter '{param_name}' with value '{param_value}'")
            
        except (OSError, UnicodeDecodeError) as e:
            log_error(f"Failed to read table file {table_file_path}: {str(e)}")
        except Exception as e:
            log_error(f"Unexpected error reading table file {table_file_path}: {str(e)}")
        
        return parameters
    
    def update_parameter_in_table(self, table_file_path: Path, param_name: str, new_value: str) -> bool:
        """
        Update a parameter value in a TMDL table file.
        
        Args:
            table_file_path: Path to the TMDL table file
            param_name: Name of the parameter to update
            new_value: New value for the parameter
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(table_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify this is the correct table
            table_name_match = self.table_name_pattern.search(content)
            if not table_name_match or table_name_match.group(1) != param_name:
                log_error(f"Parameter '{param_name}' not found in table file {table_file_path}")
                return False
            
            # Find and replace the parameter value
            old_pattern = self.parameter_pattern.search(content)
            if not old_pattern:
                log_error(f"No parameter expression found in {table_file_path}")
                return False
            
            old_value = old_pattern.group(1)
            new_expression = f'source = "{new_value}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
            
            # Replace the entire partition section
            partition_match = self.partition_pattern.search(content)
            if partition_match:
                partition_name = partition_match.group(1)
                old_partition = partition_match.group(0)
                new_partition = f'partition {partition_name} = m\n\tmode: import\n\t{new_expression}'
                
                new_content = content.replace(old_partition, new_partition)
            else:
                # Fallback: replace just the source expression
                new_content = content.replace(old_pattern.group(0), new_expression)
            
            # Write the updated content
            with open(table_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            log_info(f"Updated parameter '{param_name}' to '{new_value}' in {table_file_path}")
            return True
            
        except (OSError, UnicodeDecodeError) as e:
            log_error(f"Failed to update parameter in {table_file_path}: {str(e)}")
            return False
        except Exception as e:
            log_error(f"Unexpected error updating parameter in {table_file_path}: {str(e)}")
            return False
    
    def get_all_parameters(self, semantic_model_path: Path) -> Dict[str, str]:
        """
        Get all parameters from a TMDL semantic model.
        
        Args:
            semantic_model_path: Path to the semantic model folder
            
        Returns:
            Dictionary mapping parameter names to their current values
        """
        all_parameters = {}
        parameter_tables = self.find_parameter_tables(semantic_model_path)
        
        for table_name in parameter_tables:
            table_file = semantic_model_path / "definition" / "tables" / f"{table_name}.tmdl"
            if table_file.exists():
                table_params = self.extract_parameters_from_table(table_file)
                all_parameters.update(table_params)
        
        return all_parameters
    
    def update_parameters(self, semantic_model_path: Path, parameter_updates: Dict[str, str]) -> bool:
        """
        Update multiple parameters in a TMDL semantic model.
        
        Args:
            semantic_model_path: Path to the semantic model folder
            parameter_updates: Dictionary mapping parameter names to new values
            
        Returns:
            True if all updates were successful, False otherwise
        """
        success = True
        
        for param_name, new_value in parameter_updates.items():
            table_file = semantic_model_path / "definition" / "tables" / f"{param_name}.tmdl"
            
            if not table_file.exists():
                log_error(f"Parameter table file not found: {table_file}")
                success = False
                continue
            
            if not self.update_parameter_in_table(table_file, param_name, new_value):
                success = False
        
        return success 