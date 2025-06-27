from pathlib import Path
from ..utils.logger import log_info, log_error, log_warning
from ..utils.tmdl_parser import TMDLParser


class PBIPValidator:
    """Validator for PBIP templates and related files."""
    
    def __init__(self):
        self.tmdl_parser = TMDLParser()
    
    def validate_template(self, template_path: Path) -> bool:
        """Validate that the template path is a valid PBIP folder."""
        try:
            if not template_path.is_dir():
                log_error(f"Template path must be a directory: {template_path}")
                return False
            
            # Check for required PBIP files
            template_name = template_path.name
            pbip_file = template_path / f"{template_name}.pbip"
            if not pbip_file.exists():
                log_error(f"PBIP file not found: {pbip_file}")
                return False
            
            # Check for Report and SemanticModel folders
            report_folder = template_path / f"{template_name}.Report"
            semantic_model_folder = template_path / f"{template_name}.SemanticModel"
            
            if not report_folder.exists():
                log_error(f"Report folder not found: {report_folder}")
                return False
            
            if not semantic_model_folder.exists():
                log_error(f"SemanticModel folder not found: {semantic_model_folder}")
                return False
            
            # Detect and validate the model format
            model_format = self.tmdl_parser.detect_model_format(semantic_model_folder)
            
            if model_format == "bim":
                return self._validate_bim_format(semantic_model_folder)
            elif model_format == "tmdl":
                return self._validate_tmdl_format(semantic_model_folder)
            else:
                log_error(f"Unknown or unsupported model format in: {semantic_model_folder}")
                return False
            
        except (OSError, ValueError) as e:
            log_error(f"Template validation failed: {str(e)}")
            return False
        except Exception as e:
            log_error(f"Unexpected error during template validation: {str(e)}")
            raise
    
    def _validate_bim_format(self, semantic_model_folder: Path) -> bool:
        """Validate BIM format semantic model."""
        # Check for model.bim file
        model_bim = semantic_model_folder / "model.bim"
        if not model_bim.exists():
            log_error(f"model.bim file not found: {model_bim}")
            return False
        
        log_info(f"Validated BIM format PBIP template: {semantic_model_folder}")
        return True
    
    def _validate_tmdl_format(self, semantic_model_folder: Path) -> bool:
        """Validate TMDL format semantic model."""
        # Check for definition folder
        definition_folder = semantic_model_folder / "definition"
        if not definition_folder.exists():
            log_error(f"definition folder not found: {definition_folder}")
            return False
        
        # Check for model.tmdl file
        model_tmdl = definition_folder / "model.tmdl"
        if not model_tmdl.exists():
            log_error(f"model.tmdl file not found: {model_tmdl}")
            return False
        
        # Check for tables folder
        tables_folder = definition_folder / "tables"
        if not tables_folder.exists():
            log_error(f"tables folder not found: {tables_folder}")
            return False
        
        # Check if there are any table files
        table_files = list(tables_folder.glob("*.tmdl"))
        if not table_files:
            log_warning(f"No table files found in: {tables_folder}")
        
        log_info(f"Validated TMDL format PBIP template: {semantic_model_folder}")
        return True 