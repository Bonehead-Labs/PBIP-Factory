# Power BI Template Automation - Usage Guide

This guide provides step-by-step instructions for using the Power BI Template Automation tool to generate multiple PBIP projects from a master template.

## Prerequisites

- Python 3.9 or higher
- Power BI Desktop (for opening generated files)
- A master PBIP template with parameters defined

## Step 1: Prepare Your Master Template

Your master template should be a PBIP folder with:
- A `.pbip` file (e.g., `Example_PBIP.pbip`)
- A `.Report` folder with report files
- A `.SemanticModel` folder with `model.bim` containing parameters

### Example Template Structure
```
Example_PBIP/
├── Example_PBIP.pbip
├── Example_PBIP.Report/
│   ├── definition.pbir
│   ├── report.json
│   └── StaticResources/
└── Example_PBIP.SemanticModel/
    ├── definition.pbism
    ├── model.bim          # Contains parameters
    └── diagramLayout.json
```

### Defining Parameters in model.bim

Parameters should be defined in the `expressions` section of `model.bim`:

```json
{
  "model": {
    "expressions": [
      {
        "name": "Name",
        "expression": "\"Name A\" meta [IsParameterQuery=true, Type=\"Any\", IsParameterQueryRequired=true]"
      },
      {
        "name": "Owner", 
        "expression": "\"Owner A\" meta [IsParameterQuery=true, Type=\"Any\", IsParameterQueryRequired=true]"
      }
    ]
  }
}
```

## Step 2: Create Configuration File

Create a YAML configuration file (`pbip_config.yaml`):

```yaml
# Configuration for PBIP parameter automation
# This file defines how CSV columns map to parameters in the model.bim file

parameters:
  # String parameters
  - name: "Name"           # Must match parameter name in model.bim
    type: "string"         # Data type for validation and conversion
  
  - name: "Owner"
    type: "string"
  
  # Numeric parameters (if you add them to your model.bim)
  # - name: "Budget"
  #   type: "float"
  
  # - name: "Year"
  #   type: "integer"
  
  # Boolean parameters (if you add them to your model.bim)
  # - name: "IsActive"
  #   type: "boolean"

output:
  # Naming pattern for generated folders
  # Use any CSV column names in curly braces
  naming_pattern: "{Name}_{Owner}"
  directory: "./output"

logging:
  level: "INFO"           # Logging level: DEBUG, INFO, WARNING, ERROR
  format: "json"          # Log format: json, text
  file: "pbi_automation.log"  # Optional log file
```

**Configuration Options:**
- `parameters`: List of parameters to update
  - `name`: Parameter name (must match model.bim)
  - `type`: Parameter type (string, number, etc.)
- `output.naming_pattern`: Pattern for output folder names
- `output.directory`: Output directory path
- `logging.level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `logging.format`: Log format (json, text)
- `logging.file`: Optional log file path

## Step 3: Prepare CSV Data

Create a CSV file (`pbip_data.csv`) with your data:

```csv
Report_Name,Name,Owner
North_Report,North_Report,Marketing_Team
South_Report,South_Report,Sales_Team
East_Report,East_Report,Finance_Team
West_Report,West_Report,HR_Team
Central_Report,Central_Report,IT_Team
```

**CSV Column Mapping:**
- `Report_Name`: Used for output folder names and internal file renaming
- `Name`: Maps to the `Name` parameter in model.bim
- `Owner`: Maps to the `Owner` parameter in model.bim

## Step 4: Run the Tool

### Basic Command
```bash
pbi-automation generate \
    --template Example_PBIP \
    --config pbip_config.yaml \
    --data pbip_data.csv \
    --output-dir output
```

### With Verbose Logging
```bash
pbi-automation generate \
    --template Example_PBIP \
    --config pbip_config.yaml \
    --data pbip_data.csv \
    --output-dir output \
    --verbose
```

### Interactive Mode
```bash
pbi-automation launch
```

### Command Options
- `--template, -t`: Path to master PBIP template folder
- `--config, -c`: Path to YAML configuration file
- `--data, -d`: Path to CSV data file
- `--output-dir, -o`: Output directory for generated projects
- `--verbose, -v`: Enable verbose logging

## Step 5: Verify Output

After running the tool, check your output directory:

```
output/
├── North_Report/
│   ├── North_Report.pbip
│   ├── North_Report.Report/
│   └── North_Report.SemanticModel/
├── South_Report/
│   ├── South_Report.pbip
│   ├── South_Report.Report/
│   └── South_Report.SemanticModel/
└── ...
```

### What to Verify
1. **Folder Structure**: Each project has unique names
2. **Parameter Values**: Check `model.bim` in each `.SemanticModel` folder
3. **File References**: All internal references point to correct folders

## Step 6: Open in Power BI Desktop

1. Open Power BI Desktop
2. File → Open → Browse
3. Navigate to your output folder
4. Select any `.pbip` file (e.g., `North_Report.pbip`)
5. The project should open without errors

## Troubleshooting

### Common Issues

**Error: "Required artifact is missing"**
- **Cause**: Internal references still point to old folder names
- **Solution**: Ensure the tool completed successfully and all references were updated

**Error: "Multiple SaveChanges without transaction"**
- **Cause**: Table definition was modified incorrectly
- **Solution**: The tool should preserve table definitions as parameter references

**Error: "Cannot read definition.pbism"**
- **Cause**: File path references are incorrect
- **Solution**: Check that all internal references were updated properly

**Warning: "Failed to update references in cache.abf"**
- **Cause**: Binary file cannot be read as text
- **Solution**: This is expected - cache.abf files are deleted anyway

### Debugging Steps

1. **Check Logs**: Use `--verbose` flag for detailed logging
2. **Verify CSV Format**: Ensure column names match configuration
3. **Check Template**: Verify master template has correct structure
4. **Inspect Output**: Manually check generated files for correct references

### Manual Verification

Check these files in each generated project:

1. **`.pbip` file**: Should reference renamed folders
2. **`definition.pbir`**: Should reference renamed semantic model
3. **`model.bim`**: Should have updated parameter values
4. **Folder names**: Should match `Report_Name` from CSV

## Advanced Usage

### Custom Parameter Types

Add different parameter types to your configuration:

```yaml
parameters:
  - name: Name
    type: string
  - name: Owner
    type: string
  - name: Year
    type: integer
  - name: Budget
    type: float
  - name: IsActive
    type: boolean
```

### Large-Scale Processing

For processing many projects:

1. **Batch Processing**: Split large CSV files into smaller batches
2. **Parallel Processing**: Run multiple instances with different output directories
3. **Error Handling**: Check logs for any failed generations

### Integration with CI/CD

```bash
# Example CI/CD script
pbi-automation generate \
    --template $TEMPLATE_PATH \
    --config $CONFIG_PATH \
    --data $DATA_PATH \
    --output-dir $OUTPUT_PATH \
    --verbose

# Check exit code
if [ $? -eq 0 ]; then
    echo "PBIP generation successful"
else
    echo "PBIP generation failed"
    exit 1
fi
```

## Best Practices

1. **Backup Templates**: Always keep a backup of your master template
2. **Test Small**: Test with a few rows before processing large datasets
3. **Validate Output**: Always verify generated projects open correctly
4. **Version Control**: Use version control for configuration and data files
5. **Documentation**: Document your parameter structure and naming conventions

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the verbose logs for error details
3. Verify your template structure and configuration
4. Test with the provided example files 