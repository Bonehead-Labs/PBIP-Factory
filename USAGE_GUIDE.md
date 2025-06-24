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
    --template examples/templates/sample_template.pbip \
    --config examples/configs/sample_config.yaml \
    --data examples/data/sample_data.csv \
    --output-dir ./output
```

### 3. Validate Your Setup

```bash
# Validate all files before generation
pbi-automation validate \
    --template examples/templates/sample_template.pbip \
    --config examples/configs/sample_config.yaml \
    --data examples/data/sample_data.csv
```

## Configuration Guide

### Template File (PBIP)

Your Power BI project file should be in JSON format with parameters that can be updated:

```json
{
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
```

### Configuration File (YAML)

Define how CSV columns map to template parameters:

```yaml
parameters:
  - name: "region"           # CSV column name
    path: "report.parameters.region.value"  # JSON path in template
    type: "string"           # Data type: string, integer, float, boolean
  
  - name: "budget"
    path: "report.parameters.budget.value"
    type: "float"
  
  - name: "title"
    path: "report.name"      # Can update any JSON field
    type: "string"

output:
  format: "pbip"            # Output format: pbip or pbix
  naming_pattern: "{region}_{department}_{date_range}"  # Filename pattern
  directory: "./output"

logging:
  level: "INFO"
  format: "json"
  file: "pbi_automation.log"
```

### Data File (CSV)

Your CSV should contain columns matching the parameter names:

```csv
region,department,date_range,budget,is_active,title
North,Marketing,2024-01-01 to 2024-12-31,500000.0,true,North Marketing Report
South,Sales,2024-01-01 to 2024-12-31,750000.0,true,South Sales Report
East,Finance,2024-01-01 to 2024-12-31,300000.0,false,East Finance Report
```

## Advanced Features

### Dry Run Mode

Preview changes without generating files:

```bash
pbi-automation generate \
    --template template.pbip \
    --config config.yaml \
    --data data.csv \
    --output-dir ./output \
    --dry-run
```

### Verbose Logging

Get detailed output during processing:

```bash
pbi-automation generate \
    --template template.pbip \
    --config config.yaml \
    --data data.csv \
    --output-dir ./output \
    --verbose
```

### Custom Filename Patterns

Use any CSV column in your filename pattern:

```yaml
output:
  naming_pattern: "{region}_{department}_{timestamp}"
  # Will generate: North_Marketing_20240620_143022.pbip
```

### Type Conversion

The tool automatically converts data types:

- **string**: No conversion
- **integer**: Converts "123" → 123
- **float**: Converts "123.45" → 123.45
- **boolean**: Converts "true"/"1"/"yes" → True

## Best Practices

### 1. Template Design

- Use descriptive parameter names
- Include default values for all parameters
- Test your template in Power BI Desktop first

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
├── templates/
│   ├── sales_report.pbip
│   └── marketing_report.pbip
├── configs/
│   ├── sales_config.yaml
│   └── marketing_config.yaml
├── data/
│   ├── regions.csv
│   └── departments.csv
└── output/
    └── generated_reports/
```

## Troubleshooting

### Common Issues

1. **Parameter not found in template**
   - Check the JSON path in your config
   - Verify the template structure

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
pbi-automation validate -t template.pbip -c config.yaml -d data.csv

# List available templates
pbi-automation list-templates

# Get tool information
pbi-automation info
```

## Examples

### Example 1: Regional Sales Reports

**Template**: `sales_template.pbip`
**Config**: `regional_config.yaml`
**Data**: `regions.csv`

```bash
pbi-automation generate \
    --template templates/sales_template.pbip \
    --config configs/regional_config.yaml \
    --data data/regions.csv \
    --output-dir ./regional_reports \
    --format pbip \
    --verbose
```

### Example 2: Department Budget Reports

**Template**: `budget_template.pbip`
**Config**: `budget_config.yaml`
**Data**: `departments.csv`

```bash
pbi-automation generate \
    --template templates/budget_template.pbip \
    --config configs/budget_config.yaml \
    --data data/departments.csv \
    --output-dir ./budget_reports \
    --format pbix \
    --dry-run
```

## Integration

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Generate Power BI Reports
  run: |
    pbi-automation generate \
      --template ${{ github.workspace }}/templates/report.pbip \
      --config ${{ github.workspace }}/configs/config.yaml \
      --data ${{ github.workspace }}/data/parameters.csv \
      --output-dir ${{ github.workspace }}/output
```

### Database Integration

The tool supports database configurations (future feature):

```yaml
database:
  connection_string: "postgresql://user:pass@localhost/db"
  query: "SELECT region, department, budget FROM parameters"
```

## Support

- 📖 **Documentation**: See README.md for full documentation
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Discussions**: Join community discussions
- 📧 **Email**: support@example.com 