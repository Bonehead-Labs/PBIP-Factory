#!/bin/bash
# PBIP Template Automation - Bash Installer
# This script downloads, installs, and launches the PBIP Template Automation tool

set -e  # Exit on any error

echo "🚀 Installing PBIP Template Automation..."

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Python found: $(python --version)"
else
    echo "❌ Python not found. Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check if Git is installed
if command -v git &> /dev/null; then
    echo "✅ Git found: $(git --version)"
else
    echo "❌ Git not found. Please install Git from https://git-scm.com"
    exit 1
fi

# Ask user for installation directory
echo "Where would you like to install PBIP Template Automation?"
echo "Press Enter for default location (current directory)"
read -p "Installation directory (or press Enter for default): " install_dir

if [ -z "$install_dir" ]; then
    install_dir=$(pwd)
    echo "Using current directory: $install_dir"
else
    if [ ! -d "$install_dir" ]; then
        mkdir -p "$install_dir"
        echo "Created directory: $install_dir"
    fi
    cd "$install_dir"
fi

# Set the repository URL
REPO_URL="https://github.com/George-Nizor/_PBI_Template_Automation.git"
REPO_NAME="_PBI_Template_Automation"

# Clone or update the repository
if [ -d "$REPO_NAME" ]; then
    echo "📁 Repository already exists, updating..."
    cd "$REPO_NAME"
    git pull
else
    echo "📥 Cloning repository..."
    git clone "$REPO_URL"
    cd "$REPO_NAME"
fi

# Create and activate virtual environment
echo "🔧 Setting up virtual environment..."
if [ -d ".venv" ]; then
    echo "✅ Virtual environment already exists"
else
    $PYTHON_CMD -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install the package in editable mode
echo "📦 Installing package..."
pip install -e .

# Verify installation
echo "✅ Installation complete!"
echo "🎉 PBIP Template Automation is ready to use!"
echo "Installation location: $(pwd)"
echo ""

# Launch the CLI in interactive mode
echo "🚀 Launching PBIP Template Automation in interactive mode..."
echo ""

pbi-automation launch 