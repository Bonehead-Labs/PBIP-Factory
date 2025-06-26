from pathlib import Path
from ..utils.logger import log_info, log_error


class PBIPValidator:
    """Validator for PBIP templates and related files."""
    
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
            
            # Check for model.bim file
            model_bim = semantic_model_folder / "model.bim"
            if not model_bim.exists():
                log_error(f"model.bim file not found: {model_bim}")
                return False
            
            log_info(f"Validated PBIP template: {template_path}")
            return True
            
        except Exception as e:
            log_error(f"Template validation failed: {str(e)}")
            return False 