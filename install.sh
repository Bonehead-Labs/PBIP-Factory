#!/bin/bash
# PBIP Template Automation - Bash Installer
# This script downloads, installs, and launches the PBIP Template Automation tool

echo -e "\033[32mInstalling PBIP Template Automation...\033[0m"

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "\033[32mPython found: $PYTHON_VERSION\033[0m"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo -e "\033[32mPython found: $PYTHON_VERSION\033[0m"
    PYTHON_CMD="python"
else
    echo -e "\033[31mPython not found. Please install Python 3.9+ from https://python.org\033[0m"
    exit 1
fi

# Check if Git is installed
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version 2>&1)
    echo -e "\033[32mGit found: $GIT_VERSION\033[0m"
else
    echo -e "\033[31mGit not found. Please install Git from https://git-scm.com\033[0m"
    exit 1
fi

# Ask user for installation directory
echo -e "\033[33mWhere would you like to install PBIP Template Automation?\033[0m"
echo -e "\033[90mPress Enter for default location (current directory)\033[0m"
read -p "Installation directory (or press Enter for default): " install_dir

if [ -z "$install_dir" ]; then
    install_dir=$(pwd)
    echo -e "\033[32mUsing current directory: $install_dir\033[0m"
else
    if [ ! -d "$install_dir" ]; then
        mkdir -p "$install_dir"
        echo -e "\033[32mCreated directory: $install_dir\033[0m"
    fi
    cd "$install_dir"
fi

# Set the repository URL
repo_url="https://github.com/George-Nizor/_PBI_Template_Automation.git"
repo_name="_PBI_Template_Automation"

# Clone or update the repository
if [ -d "$repo_name" ]; then
    echo -e "\033[33mRepository already exists, checking for updates...\033[0m"
    cd "$repo_name"
    
    # Get current version before update
    current_version="unknown"
    if [ -f "pyproject.toml" ]; then
        current_version=$(grep -o 'version = "[^"]*"' pyproject.toml | cut -d'"' -f2)
    fi
    
    # Update repository
    git pull
    
    # Get new version after update
    new_version="unknown"
    if [ -f "pyproject.toml" ]; then
        new_version=$(grep -o 'version = "[^"]*"' pyproject.toml | cut -d'"' -f2)
    fi
    
    if [ "$current_version" != "$new_version" ]; then
        echo -e "\033[32mUpdated from version $current_version to $new_version\033[0m"
    else
        echo -e "\033[32mAlready up to date (version $new_version)\033[0m"
    fi
else
    echo -e "\033[33mCloning repository...\033[0m"
    git clone "$repo_url"
    cd "$repo_name"
    
    # Get version of fresh clone
    version="unknown"
    if [ -f "pyproject.toml" ]; then
        version=$(grep -o 'version = "[^"]*"' pyproject.toml | cut -d'"' -f2)
    fi
    echo -e "\033[32mInstalled version $version\033[0m"
fi

# Check if virtual environment needs recreation
recreate_venv=false
if [ -d ".venv" ]; then
    echo -e "\033[33mVirtual environment exists, checking compatibility...\033[0m"
    
    # Check Python version in venv vs current
    if [ -f ".venv/bin/python" ]; then
        venv_version=$(.venv/bin/python --version 2>&1)
        current_version=$($PYTHON_CMD --version 2>&1)
        
        if [ "$venv_version" != "$current_version" ]; then
            echo -e "\033[33mPython version changed, recreating virtual environment...\033[0m"
            echo -e "\033[90mOld: $venv_version\033[0m"
            echo -e "\033[90mNew: $current_version\033[0m"
            recreate_venv=true
        else
            echo -e "\033[32mVirtual environment is compatible\033[0m"
        fi
    else
        echo -e "\033[33mVirtual environment appears corrupted, recreating...\033[0m"
        recreate_venv=true
    fi
else
    echo -e "\033[33mCreating new virtual environment...\033[0m"
    recreate_venv=true
fi

# Create or recreate virtual environment
if [ "$recreate_venv" = true ]; then
    if [ -d ".venv" ]; then
        rm -rf .venv
        echo -e "\033[33mRemoved old virtual environment\033[0m"
    fi
    $PYTHON_CMD -m venv .venv
    echo -e "\033[32mVirtual environment created\033[0m"
fi

# Activate virtual environment
echo -e "\033[33mActivating virtual environment...\033[0m"
source .venv/bin/activate

# Install the package in editable mode
echo -e "\033[33mInstalling package...\033[0m"
pip install -e .

# Verify installation
echo -e "\033[32mInstallation complete!\033[0m"
echo -e "\033[32mPBIP Template Automation is ready to use!\033[0m"
echo -e "\033[36mInstallation location: $(pwd)\033[0m"
echo ""

# Launch the CLI in interactive mode
echo -e "\033[36mLaunching PBIP Template Automation in interactive mode...\033[0m"
echo ""

pbi-automation launch 