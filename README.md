# Power BI Template Automation

A Python tool for automating Power BI template (PBIP) generation with parameter updates. This tool takes a master PBIP template and generates multiple independent Power BI projects by updating parameters based on CSV data.

## Features

- **Template-based generation**: Use a master PBIP template as the foundation
- **Parameter automation**: Update semantic model parameters from CSV data
- **Unique project names**: Automatically rename all internal references for unique, publishable projects
- **Clean output**: Remove cache files for proper data loading
- **Simple configuration**: YAML-based configuration with CSV data input

## Quick Start

### Basic Command
python -m src.pbi_automation.cli generate --template Example_PBIP --config examples/configs/pbip_config.yaml --data examples/data/pbip_data.csv --output-dir output --verbose

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Files

- **Master Template**: A PBIP folder (e.g., `Example_PBIP/`) with parameters defined in the semantic model
- **Configuration**: YAML file defining parameters to update
- **Data**: CSV file with values for each generated project

### 3. Run the Tool

```bash
python -m src.pbi_automation.cli generate \
    --template Example_PBIP \
    --config examples/configs/pbip_config.yaml \
    --data examples/data/pbip_data.csv \
    --output-dir output \
    --verbose
```

## File Structure

```
project/
├── Example_PBIP/                    # Master template
│   ├── Example_PBIP.pbip
│   ├── Example_PBIP.Report/
│   └── Example_PBIP.SemanticModel/
├── examples/
│   ├── configs/
│   │   └── pbip_config.yaml        # Parameter configuration
│   └── data/
│       └── pbip_data.csv           # Data for generation
├── output/                          # Generated projects
│   ├── North_Report/
│   ├── South_Report/
│   └── ...
└── src/pbi_automation/              # Source code
```

## Configuration

### YAML Configuration (`pbip_config.yaml`)

```yaml
parameters:
  - name: Name
    type: string
  - name: Owner
    type: string

output:
  folder_naming: "{Name}_{Owner}"

logging:
  level: INFO
```

### CSV Data (`pbip_data.csv`)

```csv
Report_Name,Name,Owner
North_Report,North_Report,Marketing_Team
South_Report,South_Report,Sales_Team
East_Report,East_Report,Finance_Team
```

**Column mapping:**
- `Report_Name`: Used for output folder names and internal file renaming
- `Name`: Maps to the `Name` parameter in the semantic model
- `Owner`: Maps to the `Owner` parameter in the semantic model

## How It Works

1. **Copy Template**: Creates a copy of the master template for each data row
2. **Rename Files**: Renames all internal files and folders to match `Report_Name`
3. **Update References**: Updates all internal references in project files
4. **Update Parameters**: Updates parameter values in the semantic model
5. **Clean Cache**: Removes cache files for proper data loading

## Generated Output

Each generated project is:
- **Fully independent** with unique names
- **Ready for Power BI Desktop** - opens without errors
- **Ready for publishing** to Power BI Service
- **Parameterized** with updated values from CSV data

## Requirements

- Python 3.9+
- Power BI Desktop (for opening generated files)

## Dependencies

- `typer`: CLI framework
- `rich`: Terminal output formatting
- `pyyaml`: YAML configuration parsing
- `structlog`: Structured logging

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

## License

MIT License - see LICENSE file for details. 