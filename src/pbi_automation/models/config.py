from typing import List, Dict, Any, Optional, Sequence, Union
from pathlib import Path
from dataclasses import dataclass
import yaml


@dataclass
class ParameterConfig:
    """Configuration for a single parameter.

    Attributes:
        name: The parameter name as defined in the semantic model.
        type: A simple type hint for validation (e.g., "string", "integer").
    """
    name: str
    type: str = "string"


class Config:
    """Configuration for PBIP Factory runtime.

    Parameters are loaded from YAML and normalized into ParameterConfig objects.
    """
    
    def __init__(self, parameters: Sequence[Union[Dict[str, Any], ParameterConfig]], output: Optional[Dict[str, Any]] = None, logging: Optional[Dict[str, Any]] = None):
        self.parameters: List[ParameterConfig] = [self._to_parameter_config(p) for p in parameters]
        self.output: Dict[str, Any] = output or {}
        self.logging: Dict[str, Any] = logging or {}
    
    @staticmethod
    def _to_parameter_config(param: Union[Dict[str, Any], ParameterConfig]) -> ParameterConfig:
        """Normalize either a dict or ParameterConfig to a ParameterConfig instance."""
        if isinstance(param, ParameterConfig):
            return param
        if not isinstance(param, dict):
            raise ValueError("Parameter must be a dict or ParameterConfig")
        # Support both 'type' and 'value_type' (alias) in YAML
        name = param.get("name")
        if not name:
            raise ValueError("Parameter 'name' is required")
        value_type = param.get("type", param.get("value_type", "string"))
        return ParameterConfig(name=name, type=value_type)
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'Config':
        """Load configuration from a YAML file and validate structure."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError("Configuration file must contain a YAML mapping")
        parameters = data.get("parameters", [])
        output = data.get("output") or {}
        logging = data.get("logging") or {}
        if not isinstance(parameters, list):
            raise ValueError("'parameters' must be a list of parameter definitions")
        return cls(parameters=parameters, output=output, logging=logging)