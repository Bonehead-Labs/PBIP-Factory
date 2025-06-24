# Power BI Template Automation

A Python tool for programmatically generating modified Power BI project files (PBIP) based on parameterized configurations.

## Features

- 🚀 **Bulk Processing**: Generate multiple PBIP projects from a single template
- 📊 **CSV-Driven**: Use CSV files to define parameter variations
- 🔧 **Simple Configuration**: Easy YAML-based configuration
- 🎨 **Modern CLI**: Beautiful, interactive command-line interface with rich formatting
- 📁 **PBIP Focus**: Specialized for Power BI project files (PBIP folders)
- 🛡️ **Type Safety**: Built with Pydantic for robust data validation
- 📝 **Comprehensive Logging**: Structured logging with multiple output formats
- ✅ **Parameter Validation**: Automatically detects and validates PBIP parameters

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/pbi-template-automation.git
cd pbi-template-automation

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
python install.py
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

1. **Prepare your Power BI project folder (PBIP)**
2. **Create a CSV file with parameter variations**
3. **Run the automation tool**

```bash
# Basic usage
pbi-automation generate --template Example_PBIP --config config.yaml --data parameters.csv --output-dir ./output

# With verbose logging
pbi-automation generate \
    --template ./templates/sales_report \
    --config ./configs/sales_config.yaml \
    --data ./data/regions.csv \
    --output-dir ./generated_reports \
    --verbose
```

## How It Works

The tool works by:

1. **Reading** a PBIP template folder (containing `.pbip` file and subfolders)
2. **Detecting** parameters from the `model.bim` file in the SemanticModel folder
3. **Copying** the entire PBIP structure to new folders
4. **Updating** parameter values in each `model.bim` file according to your CSV data
5. **Naming** output folders using your specified pattern

## Configuration

### CSV Data Format

Your CSV file should contain columns that correspond to the parameters in your PBIP template:

```csv
Name,Owner
North_Report,Marketing_Team
South_Report,Sales_Team
East_Report,Finance_Team
West_Report,HR_Team
Central_Report,IT_Team
```

### Configuration File (YAML)

```yaml
# config.yaml
parameters:
  - name: "Name"
    type: "string"
  - name: "Owner"
    type: "string"

output:
  naming_pattern: "{Name}_{Owner}"
  directory: "./output"

logging:
  level: "INFO"
  format: "json"
  file: "pbi_automation.log"
```

## CLI Commands

### Generate PBIP Projects

```bash
pbi-automation generate [OPTIONS]
```

**Options:**
- `--template, -t`: Path to the source PBIP folder
- `--config, -c`: Path to configuration file
- `--data, -d`: Path to CSV data file
- `--output-dir, -o`: Output directory for generated folders
- `--verbose, -v`: Enable verbose logging
- `--dry-run`: Preview changes without generating files

### Validate Configuration

```bash
pbi-automation validate [OPTIONS]
```

**Options:**
- `--template, -t`: Path to the source PBIP folder
- `--config, -c`: Path to configuration file
- `--data, -d`: Path to CSV data file

### List Templates

```bash
pbi-automation list-templates [OPTIONS]
```

### Show Information

```bash
pbi-automation info
```

## Example Usage

### 1. Validate Your Setup

```bash
pbi-automation validate \
    --template Example_PBIP \
    --config examples/configs/pbip_config.yaml \
    --data examples/data/pbip_data.csv
```

### 2. Preview Changes (Dry Run)

```bash
pbi-automation generate \
    --template Example_PBIP \
    --config examples/configs/pbip_config.yaml \
    --data examples/data/pbip_data.csv \
    --dry-run
```

### 3. Generate PBIP Projects

```bash
pbi-automation generate \
    --template Example_PBIP \
    --config examples/configs/pbip_config.yaml \
    --data examples/data/pbip_data.csv \
    --output-dir ./output \
    --verbose
```

## Project Structure

```
pbi-template-automation/
├── src/
│   └── pbi_automation/
│       ├── __init__.py
│       ├── cli.py                 # Main CLI interface
│       ├── core/
│       │   ├── __init__.py
│       │   ├── processor.py       # Core processing logic
│       │   └── validator.py       # Data validation
│       ├── models/
│       │   ├── __init__.py
│       │   ├── config.py          # Configuration models
│       │   ├── data.py            # Data models
│       │   └── pbip.py            # PBIP structure models
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── logger.py          # Logging utilities
│       │   ├── file_utils.py      # File operations
│       │   └── cli_utils.py       # CLI utilities
│       └── database/
│           ├── __init__.py
│           ├── models.py          # Database models
│           └── connection.py      # Database connection
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_processor.py
│   └── test_models.py
├── examples/
│   ├── templates/
│   ├── configs/
│   └── data/
├── PBIP/                          # Example PBIP template
│   ├── Example_PBIP.pbip
│   ├── Example_PBIP.Report/
│   └── Example_PBIP.SemanticModel/
├── docs/
├── pyproject.toml
├── README.md
└── requirements.txt
```

## PBIP Template Requirements

Your PBIP template folder must contain:

1. **`.pbip` file**: The main project file (e.g., `Example_PBIP.pbip`)
2. **`.Report/` folder**: Contains report definition files
3. **`.SemanticModel/` folder**: Contains `model.bim` with parameters

The tool automatically detects parameters from the `expressions` section in `model.bim`.

## Development

### Setting up Development Environment

```bash
# Install development dependencies
python install.py

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pbi_automation --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/pbi-template-automation/issues)
- 📖 Documentation: [Wiki](https://github.com/your-org/pbi-template-automation/wiki)

## Roadmap

- [ ] Database integration for configuration storage
- [ ] Web-based configuration interface
- [ ] Template versioning and management
- [ ] Integration with Power BI Service API
- [ ] Real-time parameter validation
- [ ] Batch processing optimization 