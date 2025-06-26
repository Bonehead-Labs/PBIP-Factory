# PBIP Template Automation Tool

## 🚀 Quick Install

**Windows (PowerShell):**
```powershell
irm "https://raw.githubusercontent.com/George-Nizor/_PBI_Template_Automation/main/install.ps1" | iex
```

**Linux/Mac (Bash):**
```bash
curl -sSL https://raw.githubusercontent.com/George-Nizor/_PBI_Template_Automation/main/install.sh | bash
```

These commands will:
- Clone the repository
- Set up a Python virtual environment
- Install all dependencies
- Launch the tool in interactive mode

---

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

## Quick Start: Self-Contained Setup

Follow these steps to get started on any machine with Python 3.9+:

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd _PBI_Template_Automation
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install the project in editable mode:**
   ```sh
   pip install -e .
   ```
   This will install all dependencies and make the `pbi-automation` CLI available in your environment.

4. **Run the CLI:**
   ```sh
   pbi-automation --help
   pbi-automation launch
   pbi-automation generate ...
   ```

---

## Editable Install: What You Need to Know

- **Editable install** (`pip install -e .`) links your source code to your Python environment. Any code changes are immediately reflected in the CLI.
- If you move, rename, or delete the `src/pbi_automation` folder, the CLI will break.
- If you change the CLI entry point in `pyproject.toml`, re-run `pip install -e .`.
- If you uninstall the package or delete your virtual environment, the CLI will be removed.
- Always activate your virtual environment before running or developing.
- Re-run `pip install -e .` if you or a teammate change dependencies or entry points.

---

## Onboarding for New Developers

1. **Clone the repo and set up a virtual environment as above.**
2. **Install in editable mode:** `pip install -e .`
3. **Run the CLI:** `pbi-automation launch` or `pbi-automation generate ...`
4. **Make enhancements:** All code changes are instantly available in your CLI.
5. **If you add dependencies:** Add them to `pyproject.toml` and re-run `pip install -e .`.

---

## Troubleshooting

- If you see `ModuleNotFoundError` or missing CLI commands, ensure your virtual environment is activated and you have run `pip install -e .`.
- If you change the project structure or dependencies, re-run the install command.

---

For more details, see the [USAGE_GUIDE.md](USAGE_GUIDE.md). 