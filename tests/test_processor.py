import pytest
from pathlib import Path
import tempfile
import json
import shutil
import io

from src.pbi_automation.core.processor import PBIPProcessor
from src.pbi_automation.models.config import Config
from src.pbi_automation.models.data import DataRow, load_data_from_csv
from src.pbi_automation.core.validator import PBIPValidator


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_config():
    return Config(
        parameters=[
            {"name": "Name", "type": "string"},
            {"name": "Owner", "type": "string"}
        ],
        output={},
        logging={}
    )


@pytest.fixture
def sample_template(temp_dir):
    """Create a minimal PBIP template structure for testing."""
    template_dir = temp_dir / "Example_PBIP"
    template_dir.mkdir()
    
    # Create .pbip file
    pbip_file = template_dir / "Example_PBIP.pbip"
    pbip_content = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Example_PBIP.Report"
                }
            }
        ],
        "settings": {
            "enableAutoRecovery": True
        }
    }
    with open(pbip_file, 'w') as f:
        json.dump(pbip_content, f, indent=2)
    
    # Create Report folder
    report_dir = template_dir / "Example_PBIP.Report"
    report_dir.mkdir()
    
    # Create definition.pbir
    pbir_file = report_dir / "definition.pbir"
    pbir_content = {
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": "../Example_PBIP.SemanticModel"
            },
            "byConnection": None
        }
    }
    with open(pbir_file, 'w') as f:
        json.dump(pbir_content, f, indent=2)
    
    # Create SemanticModel folder
    semantic_dir = template_dir / "Example_PBIP.SemanticModel"
    semantic_dir.mkdir()
    
    # Create model.bim with parameters
    model_bim_file = semantic_dir / "model.bim"
    model_bim_content = {
        "compatibilityLevel": 1550,
        "model": {
            "expressions": [
                {
                    "name": "Name",
                    "expression": "\"Name A\" meta [IsParameterQuery=true, Type=\"Any\", IsParameterQueryRequired=true]",
                    "kind": "m"
                },
                {
                    "name": "Owner",
                    "expression": "\"Owner A\" meta [IsParameterQuery=true, Type=\"Any\", IsParameterQueryRequired=true]",
                    "kind": "m"
                }
            ]
        }
    }
    with open(model_bim_file, 'w') as f:
        json.dump(model_bim_content, f, indent=2)
    
    # Create definition.pbism
    pbism_file = semantic_dir / "definition.pbism"
    pbism_content = {
        "version": "4.0",
        "settings": {}
    }
    with open(pbism_file, 'w') as f:
        json.dump(pbism_content, f, indent=2)
    
    return template_dir


def test_processor_initialization(sample_config):
    """Test PBIPProcessor initialization."""
    processor = PBIPProcessor(sample_config)
    assert processor.config == sample_config


def test_process_single_row(temp_dir, sample_config, sample_template):
    """Test processing a single data row."""
    processor = PBIPProcessor(sample_config)
    
    # Create test data
    row_data = {
        "Report_Name": "Test_Report",
        "Name": "Test_Report",
        "Owner": "Test_Team"
    }
    row = DataRow(row_data)
    
    # Process the row
    output_dir = temp_dir / "output"
    output_dir.mkdir()
    
    result = processor.process_row(sample_template, row, output_dir)
    
    # Verify the result
    assert result is True
    
    # Check that output folder was created
    expected_folder = output_dir / "Test_Report"
    assert expected_folder.exists()
    
    # Check that files were renamed
    assert (expected_folder / "Test_Report.pbip").exists()
    assert (expected_folder / "Test_Report.Report").exists()
    assert (expected_folder / "Test_Report.SemanticModel").exists()
    
    # Check that parameters were updated
    model_bim_path = expected_folder / "Test_Report.SemanticModel" / "model.bim"
    with open(model_bim_path, 'r') as f:
        model_data = json.load(f)
    
    expressions = model_data["model"]["expressions"]
    name_param = next((e for e in expressions if e["name"] == "Name"), None)
    owner_param = next((e for e in expressions if e["name"] == "Owner"), None)
    
    assert name_param is not None
    assert owner_param is not None
    assert '"Test_Report"' in name_param["expression"]
    assert '"Test_Team"' in owner_param["expression"]


def test_process_multiple_rows(temp_dir, sample_config, sample_template):
    """Test processing multiple data rows."""
    processor = PBIPProcessor(sample_config)
    
    # Create test data
    rows = [
        DataRow({"Report_Name": "Report1", "Name": "Report1", "Owner": "Team1"}),
        DataRow({"Report_Name": "Report2", "Name": "Report2", "Owner": "Team2"})
    ]
    
    # Process the rows
    output_dir = temp_dir / "output"
    output_dir.mkdir()
    
    success_count = processor.process_data(sample_template, rows, output_dir)
    
    # Verify results
    assert success_count == 2
    
    # Check that both folders were created
    assert (output_dir / "Report1").exists()
    assert (output_dir / "Report2").exists()
    
    # Check that both have renamed files
    assert (output_dir / "Report1" / "Report1.pbip").exists()
    assert (output_dir / "Report2" / "Report2.pbip").exists()


def test_data_row_folder_name():
    """Test DataRow folder name generation."""
    # Test with Report_Name
    row = DataRow({"Report_Name": "My_Report", "Name": "Test", "Owner": "Team"})
    assert row.get_folder_name() == "My_Report"
    
    # Test fallback to Name_Owner
    row = DataRow({"Name": "Test", "Owner": "Team"})
    assert row.get_folder_name() == "Test_Team"


def test_validator_valid_template(sample_template):
    validator = PBIPValidator()
    assert validator.validate_template(sample_template) is True


def test_validator_invalid_template(temp_dir):
    validator = PBIPValidator()
    # Directory exists but missing required files
    bad_template = temp_dir / "BadTemplate"
    bad_template.mkdir()
    assert validator.validate_template(bad_template) is False


def test_load_data_from_csv_valid(tmp_path):
    csv_content = "Name,Owner,Report_Name\nA,Team1,ReportA\nB,Team2,ReportB\n"
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    rows = load_data_from_csv(csv_file)
    assert len(rows) == 2
    assert rows[0].get_folder_name() == "ReportA"
    assert rows[1].get_folder_name() == "ReportB" 