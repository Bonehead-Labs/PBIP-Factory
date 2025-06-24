#!/usr/bin/env python3
"""
Simple installation script for development.
"""
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install project dependencies."""
    print("Installing dependencies...")
    
    # Install from requirements.txt
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Install in development mode
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    
    print("✓ Dependencies installed successfully!")

def run_tests():
    """Run the test suite."""
    print("Running tests...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        print("✓ All tests passed!")
    except subprocess.CalledProcessError:
        print("✗ Some tests failed!")
        return False
    
    return True

def main():
    """Main installation function."""
    print("Power BI Template Automation - Development Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Run tests
    if run_tests():
        print("\n🎉 Setup completed successfully!")
        print("\nYou can now use the tool:")
        print("  pbi-automation --help")
        print("  pbi-automation info")
    else:
        print("\n⚠️  Setup completed with test failures.")
        print("Please check the test output above.")

if __name__ == "__main__":
    main() 