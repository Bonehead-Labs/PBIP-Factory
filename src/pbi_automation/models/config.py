from typing import List, Optional
from pydantic import BaseModel, Field

class ParameterConfig(BaseModel):
    """Configuration for a parameter that can be updated."""
    name: str = Field(..., description="Parameter name (must match name in model.bim)")
    type: str = Field(..., description="Parameter type: string, integer, float, boolean")

class OutputConfig(BaseModel):
    """Configuration for output settings."""
    naming_pattern: str = Field(..., description="Pattern for naming generated folders")
    directory: str = Field("./output", description="Output directory for generated folders")

class LoggingConfig(BaseModel):
    """Configuration for logging settings."""
    level: str = Field("INFO", description="Logging level")
    format: str = Field("json", description="Log format")
    file: Optional[str] = Field(None, description="Log file path")

class AppConfig(BaseModel):
    """Main application configuration."""
    parameters: List[ParameterConfig] = Field(..., description="List of parameters to update")
    output: OutputConfig = Field(..., description="Output configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration") 