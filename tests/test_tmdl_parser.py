"""
Tests for TMDL parser functionality.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.pbi_automation.utils.tmdl_parser import TMDLParser


class TestTMDLParser:
    """Test cases for TMDLParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create a TMDL parser instance."""
        return TMDLParser()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_detect_bim_format(self, parser, temp_dir):
        """Test BIM format detection."""
        # Create BIM structure
        semantic_model = temp_dir / "Test.SemanticModel"
        semantic_model.mkdir()
        model_bim = semantic_model / "model.bim"
        model_bim.write_text('{"model": {"expressions": []}}')
        
        format_type = parser.detect_model_format(semantic_model)
        assert format_type == "bim"
    
    def test_detect_tmdl_format(self, parser, temp_dir):
        """Test TMDL format detection."""
        # Create TMDL structure
        semantic_model = temp_dir / "Test.SemanticModel"
        definition = semantic_model / "definition"
        definition.mkdir(parents=True)
        model_tmdl = definition / "model.tmdl"
        model_tmdl.write_text("model Model\n\tculture: en-US")
        
        format_type = parser.detect_model_format(semantic_model)
        assert format_type == "tmdl"
    
    def test_detect_unknown_format(self, parser, temp_dir):
        """Test unknown format detection."""
        # Create empty semantic model
        semantic_model = temp_dir / "Test.SemanticModel"
        semantic_model.mkdir()
        
        format_type = parser.detect_model_format(semantic_model)
        assert format_type == "unknown"
    
    def test_find_parameter_tables(self, parser, temp_dir):
        """Test finding parameter tables in TMDL format."""
        # Create TMDL structure with parameter tables
        semantic_model = temp_dir / "Test.SemanticModel"
        definition = semantic_model / "definition"
        tables = definition / "tables"
        tables.mkdir(parents=True)
        
        # Create parameter table
        param_table = tables / "Contract_Name.tmdl"
        param_table.write_text("""
table Contract_Name
    lineageTag: a251da0c-f23e-4a35-892f-cdf1db97dc56

    column Contract_Name
        dataType: string
        lineageTag: 371fd31e-afc5-439b-b2c1-22d461084e30
        summarizeBy: none
        sourceColumn: Contract_Name

        annotation SummarizationSetBy = Automatic

    partition Contract_Name = m
        mode: import
        source = "ATCO_WA" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

    annotation PBI_NavigationStepName = Navigation

    annotation PBI_ResultType = Text
""")
        
        # Create non-parameter table
        non_param_table = tables / "Regular_Table.tmdl"
        non_param_table.write_text("""
table Regular_Table
    lineageTag: test-123

    column TestColumn
        dataType: string
        sourceColumn: TestColumn

    partition Regular_Table = m
        mode: import
        source = "SELECT * FROM test_table"
""")
        
        parameter_tables = parser.find_parameter_tables(semantic_model)
        assert "Contract_Name" in parameter_tables
        assert "Regular_Table" not in parameter_tables
    
    def test_extract_parameters_from_table(self, parser, temp_dir):
        """Test extracting parameters from a TMDL table."""
        # Create parameter table
        table_file = temp_dir / "Contract_Name.tmdl"
        table_file.write_text("""
table Contract_Name
    lineageTag: a251da0c-f23e-4a35-892f-cdf1db97dc56

    column Contract_Name
        dataType: string
        lineageTag: 371fd31e-afc5-439b-b2c1-22d461084e30
        summarizeBy: none
        sourceColumn: Contract_Name

        annotation SummarizationSetBy = Automatic

    partition Contract_Name = m
        mode: import
        source = "ATCO_WA" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

    annotation PBI_NavigationStepName = Navigation

    annotation PBI_ResultType = Text
""")
        
        parameters = parser.extract_parameters_from_table(table_file)
        assert "Contract_Name" in parameters
        assert parameters["Contract_Name"] == "ATCO_WA"
    
    def test_update_parameter_in_table(self, parser, temp_dir):
        """Test updating a parameter in a TMDL table."""
        # Create parameter table
        table_file = temp_dir / "Contract_Name.tmdl"
        original_content = """
table Contract_Name
    lineageTag: a251da0c-f23e-4a35-892f-cdf1db97dc56

    column Contract_Name
        dataType: string
        lineageTag: 371fd31e-afc5-439b-b2c1-22d461084e30
        summarizeBy: none
        sourceColumn: Contract_Name

        annotation SummarizationSetBy = Automatic

    partition Contract_Name = m
        mode: import
        source = "ATCO_WA" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

    annotation PBI_NavigationStepName = Navigation

    annotation PBI_ResultType = Text
"""
        table_file.write_text(original_content)
        
        # Update parameter
        success = parser.update_parameter_in_table(table_file, "Contract_Name", "NEW_CONTRACT")
        assert success is True
        
        # Verify the update
        updated_content = table_file.read_text()
        assert "NEW_CONTRACT" in updated_content
        assert "ATCO_WA" not in updated_content
    
    def test_get_all_parameters(self, parser, temp_dir):
        """Test getting all parameters from a TMDL semantic model."""
        # Create TMDL structure with multiple parameter tables
        semantic_model = temp_dir / "Test.SemanticModel"
        definition = semantic_model / "definition"
        tables = definition / "tables"
        tables.mkdir(parents=True)
        
        # Create first parameter table
        param1_table = tables / "Contract_Name.tmdl"
        param1_table.write_text("""
table Contract_Name
    partition Contract_Name = m
        mode: import
        source = "ATCO_WA" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
""")
        
        # Create second parameter table
        param2_table = tables / "Logo_url.tmdl"
        param2_table.write_text("""
table Logo_url
    partition Logo_url = m
        mode: import
        source = "https://example.com/logo.png" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
""")
        
        all_parameters = parser.get_all_parameters(semantic_model)
        assert "Contract_Name" in all_parameters
        assert "Logo_url" in all_parameters
        assert all_parameters["Contract_Name"] == "ATCO_WA"
        assert all_parameters["Logo_url"] == "https://example.com/logo.png"
    
    def test_update_parameters(self, parser, temp_dir):
        """Test updating multiple parameters in a TMDL semantic model."""
        # Create TMDL structure with parameter tables
        semantic_model = temp_dir / "Test.SemanticModel"
        definition = semantic_model / "definition"
        tables = definition / "tables"
        tables.mkdir(parents=True)
        
        # Create parameter table
        param_table = tables / "Contract_Name.tmdl"
        param_table.write_text("""
table Contract_Name
    partition Contract_Name = m
        mode: import
        source = "ATCO_WA" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
""")
        
        # Update parameters
        parameter_updates = {"Contract_Name": "NEW_CONTRACT"}
        success = parser.update_parameters(semantic_model, parameter_updates)
        assert success is True
        
        # Verify the update
        updated_content = param_table.read_text()
        assert "NEW_CONTRACT" in updated_content
        assert "ATCO_WA" not in updated_content 