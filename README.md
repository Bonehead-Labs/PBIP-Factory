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
- Ask where you'd like to install (or use current directory by default)
- Clone the repository
- Set up a Python virtual environment
- Install all dependencies
- Launch the tool in interactive mode

**Note:** You can specify a custom installation directory when prompted, or press Enter to use the current directory.

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

```