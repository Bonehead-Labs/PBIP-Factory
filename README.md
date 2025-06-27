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
- Install to the current directory
- Clone the repository and set up a Python virtual environment
- Install all dependencies
- Show you the commands to launch the tool

**After installation, launch the tool with:**
```bash
# Navigate to the installation directory
cd _PBI_Template_Automation

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Launch in interactive mode
pbi-automation launch
```

## 🔄 Smart Updates

The installer includes intelligent update logic:

- **Repository Updates**: Always pulls the latest code from GitHub
- **Version Tracking**: Shows version changes (e.g., "Updated from version 0.1.0 to 0.1.1")
- **Virtual Environment Management**: Automatically recreates the virtual environment if Python version changes
- **Safe Reinstallation**: Package is always reinstalled in editable mode (safe and fast)

**Reinstalling/Updating:**
- Run the same install command again - it will automatically update existing installations
- No need to manually delete or clean up previous installations
- Your configuration files and output directories are preserved

---

## Overview

A Python tool for automating Power BI template (PBIP) generation with parameter updates. This tool takes a master PBIP template and generates multiple independent Power BI projects by updating parameters based on CSV data.

## Features

- **Template-based generation**: Use a master PBIP template as the foundation
- **Parameter automation**: Update semantic model parameters from CSV data
- **Unique project names**: Automatically rename all internal references for unique, publishable projects
- **Clean output**: Remove cache files for proper data loading
- **Simple configuration**: YAML-based configuration with CSV data input
- **Interactive CLI**: User-friendly command-line interface with validation
- **Robust error handling**: Comprehensive error reporting and recovery

## Quick Start: Self-Contained Setup

Follow these steps to get started on any machine with Python 3.9+:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/George-Nizor/_PBI_Template_Automation.git
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

## Usage

### Interactive Mode
```bash
pbi-automation launch
```

### Command Line Mode
```bash
pbi-automation generate \
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

### CSV Data (`pbip_data.csv`)

```csv
Report_Name,Name,Owner
North_Report,North_Report,Marketing_Team
South_Report,South_Report,Sales_Team
East_Report,East_Report,Finance_Team
West_Report,West_Report,HR_Team
Central_Report,Central_Report,IT_Team
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
black src/
isort src/
```

## Documentation

For detailed usage instructions and troubleshooting, see [USAGE_GUIDE.md](USAGE_GUIDE.md).