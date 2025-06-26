# PBIP Template Automation - PowerShell Installer
# This script downloads, installs, and sets up the PBIP Template Automation tool

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

# Use current directory for installation
$installDir = Get-Location
Write-Host "Installing to: $installDir" -ForegroundColor Green

# Set the repository URL
$repoUrl = "https://github.com/George-Nizor/_PBI_Template_Automation.git"
$repoName = "_PBI_Template_Automation"

# Clone or update the repository
if (Test-Path $repoName) {
    Write-Host "Repository already exists, checking for updates..." -ForegroundColor Yellow
    Set-Location $repoName
    
    # Get current version before update
    $currentVersion = "unknown"
    if (Test-Path "pyproject.toml") {
        $pyprojectContent = Get-Content "pyproject.toml" -Raw
        if ($pyprojectContent -match 'version = "([^"]+)"') {
            $currentVersion = $matches[1]
        }
    }
    
    # Update repository
    git pull
    
    # Get new version after update
    $newVersion = "unknown"
    if (Test-Path "pyproject.toml") {
        $pyprojectContent = Get-Content "pyproject.toml" -Raw
        if ($pyprojectContent -match 'version = "([^"]+)"') {
            $newVersion = $matches[1]
        }
    }
    
    if ($currentVersion -ne $newVersion) {
        Write-Host "Updated from version $currentVersion to $newVersion" -ForegroundColor Green
    } else {
        Write-Host "Already up to date (version $newVersion)" -ForegroundColor Green
    }
} else {
    Write-Host "Cloning repository..." -ForegroundColor Yellow
    git clone $repoUrl
    Set-Location $repoName
    
    # Get version of fresh clone
    $version = "unknown"
    if (Test-Path "pyproject.toml") {
        $pyprojectContent = Get-Content "pyproject.toml" -Raw
        if ($pyprojectContent -match 'version = "([^"]+)"') {
            $version = $matches[1]
        }
    }
    Write-Host "Installed version $version" -ForegroundColor Green
}

# Check if virtual environment needs recreation
$recreateVenv = $false
if (Test-Path ".venv") {
    Write-Host "Virtual environment exists, checking compatibility..." -ForegroundColor Yellow
    
    # Check Python version in venv vs current
    try {
        $venvPython = ".venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            $venvVersion = & $venvPython --version 2>&1
            $currentVersion = python --version 2>&1
            
            if ($venvVersion -ne $currentVersion) {
                Write-Host "Python version changed, recreating virtual environment..." -ForegroundColor Yellow
                Write-Host "Old: $venvVersion" -ForegroundColor Gray
                Write-Host "New: $currentVersion" -ForegroundColor Gray
                $recreateVenv = $true
            } else {
                Write-Host "Virtual environment is compatible" -ForegroundColor Green
            }
        } else {
            Write-Host "Virtual environment appears corrupted, recreating..." -ForegroundColor Yellow
            $recreateVenv = $true
        }
    } catch {
        Write-Host "Error checking virtual environment, recreating..." -ForegroundColor Yellow
        $recreateVenv = $true
    }
} else {
    Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
    $recreateVenv = $true
}

# Create or recreate virtual environment
if ($recreateVenv) {
    if (Test-Path ".venv") {
        Remove-Item -Recurse -Force ".venv"
        Write-Host "Removed old virtual environment" -ForegroundColor Yellow
    }
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
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "🎉 PBIP Template Automation is ready to use!" -ForegroundColor Green
Write-Host "📁 Installation location: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Show launch instructions
Write-Host "🚀 To launch PBIP Template Automation, run:" -ForegroundColor Yellow
Write-Host "   cd $(Get-Location)" -ForegroundColor Cyan
Write-Host "   .venv\Scripts\activate" -ForegroundColor Cyan
Write-Host "   pbi-automation launch" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Or use the one-liner:" -ForegroundColor Yellow
Write-Host "   cd $(Get-Location); .venv\Scripts\activate; pbi-automation launch" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Happy automating!" -ForegroundColor Green 