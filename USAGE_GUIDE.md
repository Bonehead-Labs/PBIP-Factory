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
- A `.SemanticModel` folder with either `model.bim` (BIM format) or `definition/` folder (TMDL format)

### Example Template Structure (BIM Format)
```
templates/Example_PBIP/
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

### Example Template Structure (TMDL Format)
```
templates/Example_PBIP/
├── Example_PBIP.pbip
├── Example_PBIP.Report/
│   ├── definition.pbir
│   ├── report.json
│   └── StaticResources/
└── Example_PBIP.SemanticModel/
    ├── definition.pbism
    ├── definition/
    │   ├── model.tmdl
    │   └── tables/
    │       ├── Parameter1.tmdl    # Parameter files
    │       └── Parameter2.tmdl
    └── diagramLayout.json
```

### Defining Parameters

**For BIM Format:**
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

**For TMDL Format:**
Parameters are defined as individual table files in `definition/tables/` with `IsParameterQuery=true`:

```tmdl
table Name
    lineageTag: a251da0c-f23e-4a35-892f-cdf1db97dc56

    column Name
        dataType: string
        lineageTag: 371fd31e-afc5-439b-b2c1-22d461084e30
        summarizeBy: none
        sourceColumn: Name

        annotation SummarizationSetBy = Automatic

    partition Name = m
    mode: import
    source = "Name A" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

    annotation PBI_NavigationStepName = Navigation
    annotation PBI_ResultType = Text
```

## Step 2: Create Configuration File

Create a YAML configuration file (`configs/pbip_config.yaml`):

```yaml
# Configuration for PBIP parameter automation
# This file defines how CSV columns map to parameters in the semantic model

parameters:
  # String parameters
  - name: "Name"           # Must match parameter name in semantic model
    type: "string"         # Data type for validation and conversion
  
  - name: "Owner"
    type: "string"
  
  # Numeric parameters (if you add them to your semantic model)
  # - name: "Budget"
  #   type: "float"
  
  # - name: "Year"
  #   type: "integer"
  
  # Boolean parameters (if you add them to your semantic model)
  # - name: "IsActive"
  #   type: "boolean"

output:
  directory: "./outputs"

logging:
  level: "INFO"           # Logging level: DEBUG, INFO, WARNING, ERROR
  format: "json"          # Log format: json, text
  file: "pbi_automation.log"  # Optional log file
```

**Configuration Options:**
- `parameters`: List of parameters to update
  - `name`: Parameter name (must match semantic model)
  - `type`: Parameter type (string, number, etc.)
- `output.directory`: Output directory path
- `logging.level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `logging.format`: Log format (json, text)
- `logging.file`: Optional log file path

## Step 3: Prepare CSV Data

Create a CSV file (`data/pbip_data.csv`) with your data:

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
- `Name`: Maps to the `Name` parameter in semantic model
- `Owner`: Maps to the `Owner` parameter in semantic model

## Step 4: Run the Tool

### Basic Command
```bash
pbi-automation generate \
    --template Example_PBIP \
    --config configs/pbip_config.yaml \
    --data data/pbip_data.csv \
    --output-dir outputs
```

### With Verbose Logging
```bash
pbi-automation generate \
    --template Example_PBIP \
    --config configs/pbip_config.yaml \
    --data data/pbip_data.csv \
    --output-dir outputs \
    --verbose
```

### Interactive Mode
```bash
pbi-automation launch
```

### List Available Resources
```bash
# List available templates
pbi-automation list templates

# List available configuration files
pbi-automation list configs

# List available data files
pbi-automation list data
```

### Edit Configuration
```bash
pbi-automation edit \
    --config configs/pbip_config.yaml
```

### Command Options
- `--template, -t`: Path to master PBIP template folder
- `--config, -c`: Path to YAML configuration file
- `--data, -d`: Path to CSV data file
- `--output-dir, -o`: Output directory for generated projects
- `--verbose, -v`: Enable verbose logging
- `--interactive, -i`: Use interactive selection

## Step 5: Verify Output

After running the tool, check your output directory:

```
outputs/
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
2. **Parameter Values**: Check semantic model files in each `.SemanticModel` folder
3. **File References**: All internal references point to correct folders

## Step 6: Open in Power BI Desktop

1. Open Power BI Desktop
2. File → Open → Browse
3. Navigate to your output folder
4. Select any `.pbip` file (e.g., `North_Report.pbip`)
5. The project should open without errors
6. Refresh the data to load the updated parameters

## Troubleshooting

### Common Issues

**Error: "Required artifact is missing"**
- **Cause**: Internal references still point to old folder names
- **Solution**: Ensure the tool completed successfully and all references were updated

**Error: "Property 'semanticModel' has not been defined"**
- **Cause**: TMDL projects should not have semanticModel artifact in .pbip file
- **Solution**: The tool automatically handles this for TMDL format

**Error: "Cannot read definition.pbism"**
- **Cause**: File path references are incorrect
- **Solution**: Check that all internal references were updated properly

**Warning: "Failed to update references in cache.abf"**
- **Cause**: Binary file cannot be read as text
- **Solution**: This is normal - binary files are skipped during reference updates

**Error: "No parameters found in TMDL model"**
- **Cause**: TMDL parameter files not found or incorrectly formatted
- **Solution**: Ensure parameter tables have `IsParameterQuery=true` in their source definition

### Format Detection Issues

**Error: "Unsupported model format: unknown"**
- **Cause**: Tool cannot detect BIM or TMDL format
- **Solution**: 
  - For BIM: Ensure `model.bim` exists in `.SemanticModel` folder
  - For TMDL: Ensure `definition/` folder exists with `.tmdl` files

### CSV Issues

**Error: "Failed to load or parse CSV"**
- **Cause**: CSV file has encoding issues (BOM characters)
- **Solution**: The tool automatically handles BOM characters, but ensure CSV is UTF-8 encoded

**Error: "Row X has different columns than the first row"**
- **Cause**: CSV has inconsistent column structure
- **Solution**: Ensure all rows have the same columns

## Advanced Usage

### Interactive Mode

Use the `launch` command for a fully interactive experience:

```bash
pbi-automation launch
```

This provides:
- Interactive template selection
- Interactive configuration selection
- Interactive data file selection
- Guided setup process

### Interactive Configuration Editing

Use the `edit` command to modify your YAML configuration:

```bash
pbi-automation edit --config configs/pbip_config.yaml
```

This provides an interactive menu to:
- Add/remove parameters
- Modify output settings
- Configure logging options

### Resource Discovery

Use the `list` command to discover available resources:

```bash
# See what templates are available
pbi-automation list templates

# See what configuration files are available
pbi-automation list configs

# See what data files are available
pbi-automation list data
```

### Batch Processing

For large datasets, the tool processes each row independently. If one row fails, others continue processing. Check the output for any failed rows and their error messages.

## Best Practices

1. **Template Preparation**: Ensure your master template works correctly in Power BI Desktop before using it with the tool
2. **Parameter Naming**: Use consistent parameter names between your template and CSV data
3. **Testing**: Test with a small dataset first before processing large amounts of data
4. **Backup**: Keep a backup of your master template before making changes
5. **Organization**: Use the provided directory structure (`templates/`, `configs/`, `data/`, `outputs/`) for better organization
6. **Discovery**: Use the `list` command to discover available resources before running generation 