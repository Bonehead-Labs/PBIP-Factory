# Power BI Template Automation - Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone and install
git clone <repository-url>
cd pbi-template-automation
pip install -e .
```

### 2. Basic Usage

```bash
# Generate reports from template
pbi-automation generate \
    --template Example_PBIP \
    --config examples/configs/pbip_config.yaml \
    --data examples/data/pbip_data.csv \
    --output-dir ./output
```

### 3. Validate Your Setup

```bash
# Validate all files before generation
pbi-automation validate \
    --template Example_PBIP \
    --config examples/configs/pbip_config.yaml \
    --data examples/data/pbip_data.csv
```

## Configuration Guide

### PBIP Template Structure

Your Power BI project folder should have this structure:

```
Example_PBIP/
├── Example_PBIP.pbip
├── Example_PBIP.Report/
│   ├── definition.pbir
│   └── report.json
└── Example_PBIP.SemanticModel/
    ├── definition.pbism
    ├── diagramLayout.json
    └── model.bim  # Contains the parameters to update
```

The tool reads parameters from the `model.bim` file in the SemanticModel folder. Parameters are defined as expressions like:

```json
{
  "name": "Name",
  "expression": "\"Name A\" meta [IsParameterQuery=true, Type=\"Any\", IsParameterQueryRequired=true]"
}
```

### Configuration File (YAML)

Define how CSV columns map to parameters in the model.bim file:

```yaml
parameters:
  - name: "Name"           # CSV column name (must match parameter name in model.bim)
    type: "string"         # Data type: string, integer, float, boolean
  
  - name: "Owner"
    type: "string"

output:
  naming_pattern: "{Name}_{Owner}"  # Filename pattern using CSV columns
  directory: "./output"

logging:
  level: "INFO"
  format: "json"
  file: "pbi_automation.log"
```

### Data File (CSV)

Your CSV should contain columns matching the parameter names in your model.bim:

```csv
Name,Owner
North_Report,Marketing_Team
South_Report,Sales_Team
East_Report,Finance_Team
West_Report,HR_Team
Central_Report,IT_Team
```

## Advanced Features

### Dry Run Mode

Preview changes without generating files:

```bash
pbi-automation generate \
    --template Example_PBIP \
    --config config.yaml \
    --data data.csv \
    --output-dir ./output \
    --dry-run
```

### Verbose Logging

Get detailed output during processing:

```bash
pbi-automation generate \
    --template Example_PBIP \
    --config config.yaml \
    --data data.csv \
    --output-dir ./output \
    --verbose
```

### Custom Filename Patterns

Use any CSV column in your filename pattern:

```yaml
output:
  naming_pattern: "{Name}_{Owner}_{timestamp}"
  # Will generate: North_Report_Marketing_Team_20240620_143022/
```

### Type Conversion

The tool automatically converts data types:

- **string**: No conversion
- **integer**: Converts "123" → 123
- **float**: Converts "123.45" → 123.45
- **boolean**: Converts "true"/"1"/"yes" → True

## Best Practices

### 1. Template Design

- Use descriptive parameter names in your Power BI model
- Test your template in Power BI Desktop first
- Ensure parameters are properly defined in model.bim

### 2. Configuration Management

- Keep configurations in version control
- Use environment-specific configs
- Document parameter mappings

### 3. Data Preparation

- Validate CSV data before processing
- Use consistent data types
- Include all required columns

### 4. File Organization

```
project/
├── Example_PBIP/              # Your PBIP template
├── configs/
│   ├── regional_config.yaml
│   └── department_config.yaml
├── data/
│   ├── regions.csv
│   └── departments.csv
└── output/
    └── generated_reports/
```

## Troubleshooting

### Common Issues

1. **Parameter not found in model.bim**
   - Check that parameter names in CSV match exactly with model.bim
   - Verify the parameter exists in the SemanticModel

2. **Type conversion errors**
   - Ensure CSV data matches expected types
   - Check for empty or invalid values

3. **Missing CSV columns**
   - Verify all required parameters are in CSV
   - Check column names match config

4. **Invalid filename pattern**
   - Ensure pattern uses valid CSV column names
   - Test with sample data first

### Debug Commands

```bash
# Validate configuration
pbi-automation validate -t Example_PBIP -c config.yaml -d data.csv

# List available templates
pbi-automation list-templates

# Get tool information
pbi-automation info
```

## Examples

### Example 1: Regional Reports

**Template**: `Example_PBIP`
**Config**: `regional_config.yaml`
**Data**: `regions.csv`

```bash
pbi-automation generate \
    --template Example_PBIP \
    --config configs/regional_config.yaml \
    --data data/regions.csv \
    --output-dir ./regional_reports \
    --verbose
```

### Example 2: Department Reports

**Template**: `Example_PBIP`
**Config**: `department_config.yaml`
**Data**: `departments.csv`

```bash
pbi-automation generate \
    --template Example_PBIP \
    --config configs/department_config.yaml \
    --data data/departments.csv \
    --output-dir ./department_reports \
    --dry-run
```

## Integration

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Generate Power BI Reports
  run: |
    pbi-automation generate \
      --template ${{ github.workspace }}/Example_PBIP \
      --config ${{ github.workspace }}/configs/config.yaml \
      --data ${{ github.workspace }}/data/parameters.csv \
      --output-dir ${{ github.workspace }}/output
```

## Support

- 📖 **Documentation**: See README.md for full documentation
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Discussions**: Join community discussions
- 📧 **Email**: support@example.com 