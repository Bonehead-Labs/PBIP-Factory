from typing import Any, Dict, List
from pathlib import Path

from ..models.config import AppConfig, ParameterConfig
from ..utils.logger import log_error

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate the configuration file."""
    try:
        # Validate using Pydantic model
        app_config = AppConfig(**config)
        
        # Additional validation checks
        if not app_config.parameters:
            log_error("Configuration must contain at least one parameter")
            return False
        
        # Validate parameter names
        for param in app_config.parameters:
            if not param.name or not param.name.strip():
                log_error(f"Parameter has an empty name")
                return False
            
            # Check for valid parameter type
            if param.type not in ['string', 'integer', 'float', 'boolean']:
                log_error(f"Parameter '{param.name}' has invalid type: {param.type}")
                return False
        
        # Validate output configuration
        if not app_config.output.naming_pattern:
            log_error("Output naming pattern is required")
            return False
        
        return True
        
    except Exception as e:
        log_error(f"Configuration validation failed: {e}")
        return False

def validate_data(data: List[Dict[str, Any]]) -> bool:
    """Validate the CSV data."""
    try:
        if not data:
            log_error("Data file is empty")
            return False
        
        # Check that all rows have the same columns
        if len(data) > 1:
            first_row_keys = set(data[0].keys())
            for i, row in enumerate(data[1:], 1):
                row_keys = set(row.keys())
                if row_keys != first_row_keys:
                    log_error(f"Row {i} has different columns than the first row")
                    return False
        
        return True
        
    except Exception as e:
        log_error(f"Data validation failed: {e}")
        return False

def validate_template_structure(template_path: Path) -> bool:
    """Validate that the template path is a valid PBIP folder."""
    try:
        if not template_path.is_dir():
            log_error(f"Template path must be a directory: {template_path}")
            return False
        
        # Check for required PBIP files
        pbip_file = template_path / f"{template_path.name}.pbip"
        if not pbip_file.exists():
            log_error(f"PBIP file not found: {pbip_file}")
            return False
        
        # Check for Report and SemanticModel folders
        report_folder = template_path / f"{template_path.name}.Report"
        semantic_model_folder = template_path / f"{template_path.name}.SemanticModel"
        
        if not report_folder.exists():
            log_error(f"Report folder not found: {report_folder}")
            return False
        
        if not semantic_model_folder.exists():
            log_error(f"SemanticModel folder not found: {semantic_model_folder}")
            return False
        
        # Check for model.bim file
        model_bim = semantic_model_folder / "model.bim"
        if not model_bim.exists():
            log_error(f"model.bim file not found: {model_bim}")
            return False
        
        return True
        
    except Exception as e:
        log_error(f"Template validation failed: {e}")
        return False

def validate_parameter_types(data: List[Dict[str, Any]], config: AppConfig) -> List[str]:
    """Validate that data values match their expected types."""
    errors = []
    
    for i, row in enumerate(data):
        for param in config.parameters:
            if param.name in row:
                value = row[param.name]
                
                # Type validation
                if param.type == "integer":
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        errors.append(f"Row {i+1}, column '{param.name}': '{value}' is not a valid integer")
                
                elif param.type == "float":
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Row {i+1}, column '{param.name}': '{value}' is not a valid float")
                
                elif param.type == "boolean":
                    if isinstance(value, str):
                        if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
                            errors.append(f"Row {i+1}, column '{param.name}': '{value}' is not a valid boolean")
    
    return errors

def validate_filename_pattern(pattern: str, sample_data: Dict[str, Any]) -> bool:
    """Validate that the filename pattern can be formatted with the data."""
    try:
        # Test with sample data
        test_filename = pattern.format(**sample_data)
        return True
    except KeyError as e:
        log_error(f"Filename pattern references unknown parameter: {e}")
        return False
    except Exception as e:
        log_error(f"Invalid filename pattern: {e}")
        return False 