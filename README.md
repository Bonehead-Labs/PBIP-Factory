## PBIP Template Automation

Automate generation of Power BI PBIP projects from a master template with parameterized updates. Given a single PBIP template and a CSV of parameter values, this tool produces multiple, independent, ready-to-open Power BI projects.

Designed with reliability and clarity in mind, following conventions you’ll recognize from major open-source projects.

## Contents

- Overview
- Features
- Quick Start (one-line install)
- Installation (uv or pip)
- Usage (CLI and interactive)
- Configuration (YAML + CSV)
- Template Requirements (BIM/TMDL)
- How It Works
- Project Structure
- Development
- Contributing
- License

## 🚀 Quick Start (one-line install)

Use the platform installer to set up everything automatically in the current directory.

Windows (PowerShell):
```powershell
irm "https://raw.githubusercontent.com/Bonehead-Labs/PBIP-Factory/main/install.ps1" | iex
```

Linux/Mac (Bash):
```bash
curl -sSL https://raw.githubusercontent.com/Bonehead-Labs/PBIP-Factory/main/install.sh | bash
```

These installers will:
- Clone the repository
- Create a virtual environment
- Install all dependencies
- Print next-step commands (activate venv and run the CLI)

After installation:
```bash
# Navigate to the installation directory
cd PBIP-Factory

# Activate the virtual environment
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Launch in interactive mode
pbip-factory launch
```

## Features

- Template-driven PBIP project generation
- CSV-parameter automation
- Dual semantic model support: BIM and TMDL
- Automatic format detection and validation
- End-to-end project renaming and reference updates
- Cache cleanup for reliable data refresh
- Interactive and non-interactive CLI
- Resource discovery (templates/configs/data)
- Interactive YAML editor

## Requirements

- Python 3.9+
- Power BI Desktop (to open generated PBIP projects)

## Installation

### Option A: Using uv (recommended)

```bash
git clone https://github.com/Bonehead-Labs/PBIP-Factory.git
cd PBIP-Factory

# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install the project (runtime only)
uv pip install -e .

# Optional: development extras
uv pip install -e ".[dev]"
```

### Option B: Using pip

```bash
git clone https://github.com/Bonehead-Labs/PBIP-Factory.git
cd PBIP-Factory

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e .
# Optional: development extras
pip install -e ".[dev]"
```

## Usage

### Interactive mode
```bash
pbip-factory launch
```

### Command examples
```bash
# Generate PBIP projects from a template
pbip-factory generate \
  --template Example_PBIP \
  --config configs/pbip_config.yaml \
  --data data/pbip_data.csv \
  --output-dir outputs \
  --verbose

# Discover available resources
pbip-factory list templates
pbip-factory list configs
pbip-factory list data

# Inspect template format and parameters
pbip-factory detect --template templates/Example_PBIP

# Edit configuration interactively
pbip-factory edit --config configs/pbip_config.yaml

# Version
pbip-factory version
```

### Command options

- `--template, -t`: Template name or path to PBIP folder
- `--config, -c`: Path or name of YAML config
- `--data, -d`: Path or name of CSV data
- `--output-dir, -o`: Output directory for generated projects
- `--verbose, -v`: Verbose logging
- `--interactive, -i`: Guided selection UI

## Configuration

### YAML (`configs/pbip_config.yaml`)
```yaml
# Configuration for PBIP parameter automation
# Map CSV columns to semantic model parameters

parameters:
  - name: "Name"
    type: "string"
  - name: "Owner"
    type: "string"

output:
  directory: "./outputs"

logging:
  level: "INFO"    # DEBUG, INFO, WARNING, ERROR
  format: "json"   # json, text
  file: "pbi_automation.log"
```

### CSV (`data/pbip_data.csv`)
```csv
Report_Name,Name,Owner
North_Report,North_Report,Marketing_Team
South_Report,South_Report,Sales_Team
East_Report,East_Report,Finance_Team
West_Report,West_Report,HR_Team
Central_Report,Central_Report,IT_Team
```

Column mapping:
- `Report_Name`: Used for output folder names and internal renaming
- `Name`: Parameter in the semantic model
- `Owner`: Parameter in the semantic model

## Template Requirements

The master PBIP folder must include:

### BIM format (legacy)
- `Example_PBIP.pbip`
- `Example_PBIP.Report/`
- `Example_PBIP.SemanticModel/model.bim` (parameters in `model.expressions`)

### TMDL format (modern)
- `Example_PBIP.pbip`
- `Example_PBIP.Report/`
- `Example_PBIP.SemanticModel/definition/model.tmdl`
- `Example_PBIP.SemanticModel/definition/tables/*.tmdl` (parameter tables with `IsParameterQuery=true`)

The tool auto-detects BIM vs. TMDL and applies the appropriate update logic.

## How It Works

1. Copies the template for each CSV row
2. Renames `.pbip`, `.Report`, `.SemanticModel` and internal references
3. Updates parameter values (BIM `model.bim` or TMDL tables)
4. Removes `.pbi/cache.abf` to ensure a clean refresh

## Project Structure

```
project/
├── templates/
│   └── Example_PBIP/
├── configs/
│   ├── pbip_config.yaml
│   └── example_config.yaml
├── data/
│   └── pbip_data.csv
├── outputs/
└── src/pbi_automation/
```

## Development

Using uv:
```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
uv run pytest -q
```

Formatting:
```bash
black src/
isort src/
```

## Contributing

Contributions are welcome. Please open an issue to discuss changes, or submit a PR with a clear description and tests where applicable.

## License

MIT License. See the `pyproject.toml` for license metadata.