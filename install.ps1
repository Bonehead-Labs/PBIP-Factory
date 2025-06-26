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

# Ask user for installation directory
Write-Host "Where would you like to install PBIP Template Automation?" -ForegroundColor Yellow
Write-Host "Press Enter for default location (current directory)" -ForegroundColor Gray
$installDir = Read-Host "Installation directory (or press Enter for default)"

if ([string]::IsNullOrWhiteSpace($installDir)) {
    $installDir = Get-Location
    Write-Host "Using current directory: $installDir" -ForegroundColor Green
} else {
    if (-not (Test-Path $installDir)) {
        try {
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
            Write-Host "Created directory: $installDir" -ForegroundColor Green
        } catch {
            Write-Host "Failed to create directory: $installDir" -ForegroundColor Red
            exit 1
        }
    }
    Set-Location $installDir
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
Write-Host "Installation location: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Launch the CLI in interactive mode
Write-Host "Launching PBIP Template Automation in interactive mode..." -ForegroundColor Cyan
Write-Host ""

pbi-automation launch 