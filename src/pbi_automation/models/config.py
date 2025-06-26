from typing import List, Dict, Any
from pathlib import Path
import yaml


class ParameterConfig:
    """Configuration for a single parameter."""
    
    def __init__(self, name: str, type: str = "string"):
        self.name = name
        self.type = type


class Config:
    """Configuration for the PBIP automation."""
    
    def __init__(self, parameters: List[Dict[str, Any]], output: Dict[str, Any] = None, logging: Dict[str, Any] = None):
        self.parameters = [ParameterConfig(**param) for param in parameters]
        self.output = output or {}
        self.logging = logging or {}
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'Config':
        """Load configuration from a YAML file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(**data) 