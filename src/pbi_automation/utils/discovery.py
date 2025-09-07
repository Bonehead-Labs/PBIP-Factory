"""
Discovery utilities for finding available templates, configs, and data files.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .logger import log_info, log_error, log_warning


class DiscoveryManager:
    """Manages discovery of available templates, configs, and data files."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize with project root path."""
        if project_root is None:
            # Try to find project root by looking for pyproject.toml
            current = Path.cwd()
            while current != current.parent:
                if (current / "pyproject.toml").exists():
                    project_root = current
                    break
                current = current.parent
            
            if project_root is None:
                project_root = Path.cwd()
        
        self.project_root = project_root
        self.templates_dir = project_root / "templates"
        self.configs_dir = project_root / "configs"
        self.data_dir = project_root / "data"
        self.outputs_dir = project_root / "outputs"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create the new directory structure if it doesn't exist."""
        for directory in [self.templates_dir, self.configs_dir, self.data_dir, self.outputs_dir]:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                log_info(f"Created directory: {directory}")
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates."""
        templates = []
        
        # Check new templates directory
        if self.templates_dir.exists():
            for item in self.templates_dir.iterdir():
                if item.is_dir() and self._is_valid_template(item):
                    templates.append({
                        "name": item.name,
                        "path": str(item),
                        "type": "new"
                    })
        
        # Optional legacy discovery behind env flag
        if os.getenv("PBIP_LEGACY_DISCOVERY") == "1":
            legacy_locations = [
                self.project_root / "Example_PBIP",
                self.project_root / "POC for changing LINK contracts"
            ]
            for legacy_path in legacy_locations:
                if legacy_path.exists() and self._is_valid_template(legacy_path):
                    templates.append({
                        "name": legacy_path.name,
                        "path": str(legacy_path),
                        "type": "legacy"
                    })
        
        return templates
    
    def get_available_configs(self) -> List[Dict[str, str]]:
        """Get list of available configuration files."""
        configs = []
        
        # Check new configs directory
        if self.configs_dir.exists():
            for item in self.configs_dir.iterdir():
                if item.is_file() and item.suffix.lower() in ['.yaml', '.yml']:
                    configs.append({
                        "name": item.stem,
                        "path": str(item),
                        "type": "new"
                    })
        
        # Optional legacy examples/configs
        if os.getenv("PBIP_LEGACY_DISCOVERY") == "1":
            legacy_configs_dir = self.project_root / "examples" / "configs"
            if legacy_configs_dir.exists():
                for item in legacy_configs_dir.iterdir():
                    if item.is_file() and item.suffix.lower() in ['.yaml', '.yml']:
                        configs.append({
                            "name": item.stem,
                            "path": str(item),
                            "type": "legacy"
                        })
        
        return configs
    
    def get_available_data_files(self) -> List[Dict[str, str]]:
        """Get list of available data files."""
        data_files = []
        
        # Check new data directory
        if self.data_dir.exists():
            for item in self.data_dir.iterdir():
                if item.is_file() and item.suffix.lower() == '.csv':
                    data_files.append({
                        "name": item.stem,
                        "path": str(item),
                        "type": "new"
                    })
        
        # Optional legacy examples/data
        if os.getenv("PBIP_LEGACY_DISCOVERY") == "1":
            legacy_data_dir = self.project_root / "examples" / "data"
            if legacy_data_dir.exists():
                for item in legacy_data_dir.iterdir():
                    if item.is_file() and item.suffix.lower() == '.csv':
                        data_files.append({
                            "name": item.stem,
                            "path": str(item),
                            "type": "legacy"
                        })
        
        return data_files
    
    def _is_valid_template(self, template_path: Path) -> bool:
        """Check if a directory is a valid PBIP template."""
        if not template_path.is_dir():
            return False
        
        # Check for .pbip file
        pbip_files = list(template_path.glob("*.pbip"))
        if not pbip_files:
            return False
        
        # Check for .Report directory
        report_dirs = [d for d in template_path.iterdir() if d.is_dir() and d.name.endswith('.Report')]
        if not report_dirs:
            return False
        
        # Check for .SemanticModel directory
        semantic_dirs = [d for d in template_path.iterdir() if d.is_dir() and d.name.endswith('.SemanticModel')]
        if not semantic_dirs:
            return False
        
        return True
    
    def get_template_path(self, template_name: str) -> Optional[Path]:
        """Get the full path for a template by name."""
        templates = self.get_available_templates()
        for template in templates:
            if template["name"] == template_name:
                return Path(template["path"])
        return None
    
    def get_config_path(self, config_name: str) -> Optional[Path]:
        """Get the full path for a config by name."""
        configs = self.get_available_configs()
        for config in configs:
            if config["name"] == config_name:
                return Path(config["path"])
        return None
    
    def get_data_path(self, data_name: str) -> Optional[Path]:
        """Get the full path for a data file by name."""
        data_files = self.get_available_data_files()
        for data_file in data_files:
            if data_file["name"] == data_name:
                return Path(data_file["path"])
        return None
    
    def get_output_path(self, template_name: str, custom_output_dir: Optional[str] = None) -> Path:
        """Get the output path for a template."""
        if custom_output_dir:
            return Path(custom_output_dir)
        
        # Create template-specific output directory
        output_dir = self.outputs_dir / f"{template_name}_OUTPUTS"
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        return output_dir
    
    def format_template_list(self, templates: List[Dict[str, str]]) -> str:
        """Format template list for display."""
        if not templates:
            return "No templates found."
        
        lines = ["Available templates:"]
        for template in templates:
            type_indicator = "🆕" if template["type"] == "new" else "📁"
            lines.append(f"  {type_indicator} {template['name']}")
        
        return "\n".join(lines)
    
    def format_config_list(self, configs: List[Dict[str, str]]) -> str:
        """Format config list for display."""
        if not configs:
            return "No configuration files found."
        
        lines = ["Available configuration files:"]
        for config in configs:
            type_indicator = "🆕" if config["type"] == "new" else "📁"
            lines.append(f"  {type_indicator} {config['name']}")
        
        return "\n".join(lines)
    
    def format_data_list(self, data_files: List[Dict[str, str]]) -> str:
        """Format data file list for display."""
        if not data_files:
            return "No data files found."
        
        lines = ["Available data files:"]
        for data_file in data_files:
            type_indicator = "🆕" if data_file["type"] == "new" else "📁"
            lines.append(f"  {type_indicator} {data_file['name']}")
        
        return "\n".join(lines) 