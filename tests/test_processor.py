import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import json

from pbi_automation.core.processor import PBIPProcessor
from pbi_automation.models.config import AppConfig, ParameterConfig, OutputConfig

@pytest.fixture
def sample_config():
    return {
        "parameters": [
            {
                "name": "region",
                "path": "report.parameters.region.value",
                "type": "string"
            },
            {
                "name": "budget",
                "path": "report.parameters.budget.value",
                "type": "float"
            }
        ],
        "output": {
            "format": "pbip",
            "naming_pattern": "{region}_report",
            "directory": "./output"
        }
    }

@pytest.fixture
def sample_template():
    return {
        "version": "1.0",
        "report": {
            "name": "Sample Report",
            "parameters": {
                "region": {
                    "name": "Region",
                    "type": "string",
                    "value": "North"
                },
                "budget": {
                    "name": "Budget",
                    "type": "float",
                    "value": 1000000.0
                }
            }
        }
    }

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

def test_pbip_processor_initialization(temp_dir, sample_config, sample_template):
    """Test PBIPProcessor initialization."""
    # Create a temporary template file
    template_file = temp_dir / "template.pbip"
    with open(template_file, 'w') as f:
        json.dump(sample_template, f)
    
    processor = PBIPProcessor(template_file, sample_config, temp_dir)
    
    assert processor.template_path == template_file
    assert processor.output_dir == temp_dir
    assert processor.template_data == sample_template
    assert isinstance(processor.config, AppConfig)

def test_update_nested_dict():
    """Test nested dictionary update functionality."""
    processor = PBIPProcessor(Mock(), {}, Mock())
    
    data = {"a": {"b": {"c": 1}}}
    
    # Test successful update
    result = processor._update_nested_dict(data, "a.b.c", 2)
    assert result is True
    assert data["a"]["b"]["c"] == 2
    
    # Test creating new path
    result = processor._update_nested_dict(data, "x.y.z", 3)
    assert result is True
    assert data["x"]["y"]["z"] == 3
    
    # Test invalid path
    result = processor._update_nested_dict(data, "", 4)
    assert result is False

def test_generate_filename(temp_dir, sample_config, sample_template):
    """Test filename generation."""
    template_file = temp_dir / "template.pbip"
    with open(template_file, 'w') as f:
        json.dump(sample_template, f)
    
    processor = PBIPProcessor(template_file, sample_config, temp_dir)
    
    row = {"region": "North", "budget": 500000.0}
    filename = processor._generate_filename(row)
    
    assert filename == "North_report.pbip"

def test_apply_parameter_updates(temp_dir, sample_config, sample_template):
    """Test parameter updates application."""
    template_file = temp_dir / "template.pbip"
    with open(template_file, 'w') as f:
        json.dump(sample_template, f)
    
    processor = PBIPProcessor(template_file, sample_config, temp_dir)
    
    row = {"region": "South", "budget": 750000.0}
    updated_data = processor._apply_parameter_updates(processor.template_data, row)
    
    assert updated_data["report"]["parameters"]["region"]["value"] == "South"
    assert updated_data["report"]["parameters"]["budget"]["value"] == 750000.0

def test_process_row(temp_dir, sample_config, sample_template):
    """Test processing a single row."""
    template_file = temp_dir / "template.pbip"
    with open(template_file, 'w') as f:
        json.dump(sample_template, f)
    
    processor = PBIPProcessor(template_file, sample_config, temp_dir)
    
    row = {"region": "East", "budget": 300000.0}
    output_file = processor.process_row(row)
    
    assert output_file.exists()
    assert output_file.name == "East_report.pbip"
    
    # Verify the content was updated
    with open(output_file, 'r') as f:
        content = json.load(f)
    
    assert content["report"]["parameters"]["region"]["value"] == "East"
    assert content["report"]["parameters"]["budget"]["value"] == 300000.0

def test_validate_parameters(temp_dir, sample_config, sample_template):
    """Test parameter validation."""
    template_file = temp_dir / "template.pbip"
    with open(template_file, 'w') as f:
        json.dump(sample_template, f)
    
    processor = PBIPProcessor(template_file, sample_config, temp_dir)
    
    # Test with all parameters present
    row = {"region": "North", "budget": 500000.0}
    missing = processor.validate_parameters(row)
    assert missing == []
    
    # Test with missing parameters
    row = {"region": "North"}
    missing = processor.validate_parameters(row)
    assert "budget" in missing

def test_get_parameter_summary(temp_dir, sample_config, sample_template):
    """Test parameter summary generation."""
    template_file = temp_dir / "template.pbip"
    with open(template_file, 'w') as f:
        json.dump(sample_template, f)
    
    processor = PBIPProcessor(template_file, sample_config, temp_dir)
    
    row = {"region": "North", "budget": 500000.0}
    summary = processor.get_parameter_summary(row)
    
    assert "region" in summary
    assert "budget" in summary
    assert summary["region"]["value"] == "North"
    assert summary["budget"]["value"] == 500000.0

def test_type_conversion(temp_dir, sample_config, sample_template):
    """Test type conversion for different parameter types."""
    template_file = temp_dir / "template.pbip"
    with open(template_file, 'w') as f:
        json.dump(sample_template, f)
    
    processor = PBIPProcessor(template_file, sample_config, temp_dir)
    
    # Test string to integer conversion
    row = {"region": "North", "budget": "500000"}
    updated_data = processor._apply_parameter_updates(processor.template_data, row)
    assert updated_data["report"]["parameters"]["budget"]["value"] == 500000.0
    
    # Test boolean conversion
    config_with_bool = sample_config.copy()
    config_with_bool["parameters"].append({
        "name": "is_active",
        "path": "report.parameters.isActive.value",
        "type": "boolean"
    })
    
    processor.config = AppConfig(**config_with_bool)
    row = {"region": "North", "budget": 500000.0, "is_active": "true"}
    updated_data = processor._apply_parameter_updates(processor.template_data, row)
    assert updated_data["report"]["parameters"]["isActive"]["value"] is True 