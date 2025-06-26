# PBIP Template Automation - PowerShell Installer
# This script downloads, installs, and launches the PBIP Template Automation tool

Write-Host "Installing PBIP Template Automation..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.9+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if Git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git not found. Please install Git from https://git-scm.com" -ForegroundColor Red
    exit 1
}

# Set the repository URL
$repoUrl = "https://github.com/George-Nizor/_PBI_Template_Automation.git"
$repoName = "_PBI_Template_Automation"

# Clone or update the repository
if (Test-Path $repoName) {
    Write-Host "Repository already exists, updating..." -ForegroundColor Yellow
    Set-Location $repoName
    git pull
} else {
    Write-Host "Cloning repository..." -ForegroundColor Yellow
    git clone $repoUrl
    Set-Location $repoName
}

# Create and activate virtual environment
Write-Host "Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv .venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.venv\Scripts\activate

# Install the package in editable mode
Write-Host "Installing package..." -ForegroundColor Yellow
pip install -e .

# Verify installation
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "PBIP Template Automation is ready to use!" -ForegroundColor Green
Write-Host ""

# Launch the CLI in interactive mode
Write-Host "Launching PBIP Template Automation in interactive mode..." -ForegroundColor Cyan
Write-Host ""

pbi-automation launch 