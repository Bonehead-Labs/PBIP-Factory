"""
YAML Configuration Editor for PBIP Automation Tool.

This module provides interactive editing capabilities for YAML configuration files,
with validation, backup, and user-friendly interfaces.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from .cli_utils import (
    show_error_message, show_info_message, show_success_message, 
    show_warning_message, console
)
from .logger import log_info, log_error, log_warning


class YAMLFileManager:
    """Manages YAML file operations with validation and backup capabilities."""
    
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.backup_path = self.file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        self._data: Optional[CommentedMap] = None
    
    def load(self) -> bool:
        """Load YAML file with error handling."""
        try:
            if not self.file_path.exists():
                show_error_message(f"Configuration file not found: {self.file_path}")
                return False
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._data = self.yaml.load(f)
            
            if self._data is None:
                self._data = CommentedMap()
            
            log_info(f"Loaded YAML configuration from: {self.file_path}")
            return True
            
        except Exception as e:
            show_error_message(f"Failed to load YAML file: {e}")
            log_error(f"YAML load error: {e}")
            return False
    
    def save(self, create_backup: bool = True) -> bool:
        """Save YAML file with optional backup."""
        try:
            if self._data is None:
                show_error_message("No data to save")
                return False
            
            # Create backup if requested
            if create_backup and self.file_path.exists():
                shutil.copy2(self.file_path, self.backup_path)
                log_info(f"Created backup: {self.backup_path}")
            
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the file
            with open(self.file_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(self._data, f)
            
            show_success_message(f"Configuration saved to: {self.file_path}")
            log_info(f"Saved YAML configuration to: {self.file_path}")
            return True
            
        except Exception as e:
            show_error_message(f"Failed to save YAML file: {e}")
            log_error(f"YAML save error: {e}")
            return False
    
    def get_data(self) -> CommentedMap:
        """Get the current data."""
        if self._data is None:
            self._data = CommentedMap()
        return self._data
    
    def set_data(self, data: CommentedMap) -> None:
        """Set the current data."""
        self._data = data
    
    def validate_structure(self) -> bool:
        """Validate the YAML structure."""
        try:
            data = self.get_data()
            
            # Check for required top-level keys
            required_keys = ['parameters']
            for key in required_keys:
                if key not in data:
                    show_warning_message(f"Missing required key: {key}")
                    return False
            
            # Validate parameters structure
            parameters = data.get('parameters', [])
            if not isinstance(parameters, list):
                show_error_message("Parameters must be a list")
                return False
            
            for i, param in enumerate(parameters):
                if not isinstance(param, dict):
                    show_error_message(f"Parameter {i} must be a dictionary")
                    return False
                
                if 'name' not in param:
                    show_error_message(f"Parameter {i} missing 'name' field")
                    return False
                
                if 'type' not in param:
                    show_error_message(f"Parameter {i} missing 'type' field")
                    return False
            
            return True
            
        except Exception as e:
            show_error_message(f"Validation error: {e}")
            return False
    
    def create_default_config(self) -> CommentedMap:
        """Create a default configuration structure."""
        default_config = CommentedMap()
        
        # Parameters section
        default_config['parameters'] = [
            CommentedMap([('name', 'Name'), ('type', 'string')]),
            CommentedMap([('name', 'Owner'), ('type', 'string')])
        ]
        
        # Output section
        default_config['output'] = CommentedMap([
            ('directory', './output')
        ])
        
        # Logging section
        default_config['logging'] = CommentedMap([
            ('level', 'INFO'),
            ('format', 'json'),
            ('file', 'pbi_automation.log')
        ])
        
        # Add comments
        default_config.yaml_add_eol_comment('Configuration for PBIP parameter automation', 0)
        default_config.yaml_add_eol_comment('This file defines how CSV columns map to parameters in the model.bim file', 0)
        
        return default_config


class InteractiveEditor:
    """Interactive YAML configuration editor."""
    
    def __init__(self, file_path: Path):
        self.file_manager = YAMLFileManager(file_path)
        self.unsaved_changes = False
    
    def start(self) -> bool:
        """Start the interactive editor."""
        show_info_message("Starting YAML Configuration Editor")
        
        # Load existing configuration or create new one
        if not self.file_manager.load():
            if not self._create_new_config():
                return False
        
        # Main editor loop
        while True:
            try:
                choice = self._show_main_menu()
                
                if choice == '1':
                    self._edit_parameters()
                elif choice == '2':
                    self._edit_output_settings()
                elif choice == '3':
                    self._edit_logging_config()
                elif choice == '4':
                    self._view_configuration()
                elif choice == '5':
                    return self._save_and_exit()
                elif choice == '6':
                    return self._exit_without_saving()
                else:
                    show_error_message("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                return self._handle_interrupt()
            except Exception as e:
                show_error_message(f"An error occurred: {e}")
                log_error(f"Editor error: {e}")
    
    def _create_new_config(self) -> bool:
        """Create a new configuration file."""
        questions = [
            {
                'type': 'confirm',
                'name': 'create_new',
                'message': f'Configuration file not found. Create new file at {self.file_manager.file_path}?',
                'default': True
            }
        ]
        
        import inquirer
        answers = inquirer.prompt(questions)
        
        if answers and answers['create_new']:
            default_config = self.file_manager.create_default_config()
            self.file_manager.set_data(default_config)
            self.unsaved_changes = True
            show_success_message("Created new configuration with default values")
            return True
        else:
            show_info_message("Configuration creation cancelled")
            return False
    
    def _show_main_menu(self) -> str:
        """Display the main editor menu."""
        console.print()
        console.print("┌─ YAML Configuration Editor ──────────────────────┐")
        console.print("│                                                  │")
        console.print("│  What would you like to edit?                   │")
        console.print("│                                                  │")
        console.print("│  [1] Parameters                                 │")
        console.print("│  [2] Output Settings                            │")
        console.print("│  [3] Logging Configuration                      │")
        console.print("│  [4] View Current Configuration                 │")
        console.print("│  [5] Save and Exit                              │")
        console.print("│  [6] Exit Without Saving                        │")
        console.print("│                                                  │")
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
        
        import inquirer
        questions = [
            inquirer.List('choice',
                         message='Select an option',
                         choices=['1', '2', '3', '4', '5', '6'])
        ]
        
        answers = inquirer.prompt(questions)
        return answers['choice'] if answers else '6'
    
    def _edit_parameters(self) -> None:
        """Edit parameters section."""
        show_info_message("Parameter Editor")
        # TODO: Implement parameter editing
        show_warning_message("Parameter editing not yet implemented")
    
    def _edit_output_settings(self) -> None:
        """Edit output settings."""
        show_info_message("Output Settings Editor")
        # TODO: Implement output settings editing
        show_warning_message("Output settings editing not yet implemented")
    
    def _edit_logging_config(self) -> None:
        """Edit logging configuration."""
        show_info_message("Logging Configuration Editor")
        # TODO: Implement logging configuration editing
        show_warning_message("Logging configuration editing not yet implemented")
    
    def _view_configuration(self) -> None:
        """View current configuration."""
        console.print()
        console.print("┌─ Current Configuration ─────────────────────────┐")
        
        data = self.file_manager.get_data()
        
        # Display parameters
        console.print("│  [bold cyan]Parameters:[/bold cyan]")
        parameters = data.get('parameters', [])
        for param in parameters:
            name = param.get('name', 'Unknown')
            param_type = param.get('type', 'Unknown')
            console.print(f"│    - {name} ({param_type})")
        
        # Display output settings
        console.print("│  [bold cyan]Output:[/bold cyan]")
        output = data.get('output', {})
        directory = output.get('directory', './output')
        console.print(f"│    Directory: {directory}")
        
        # Display logging settings
        console.print("│  [bold cyan]Logging:[/bold cyan]")
        logging = data.get('logging', {})
        level = logging.get('level', 'INFO')
        format_type = logging.get('format', 'json')
        log_file = logging.get('file', 'pbi_automation.log')
        console.print(f"│    Level: {level}")
        console.print(f"│    Format: {format_type}")
        console.print(f"│    File: {log_file}")
        
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
    
    def _save_and_exit(self) -> bool:
        """Save configuration and exit."""
        if self.unsaved_changes:
            if self.file_manager.save():
                show_success_message("Configuration saved successfully")
                return True
            else:
                show_error_message("Failed to save configuration")
                return False
        else:
            show_info_message("No changes to save")
            return True
    
    def _exit_without_saving(self) -> bool:
        """Exit without saving changes."""
        if self.unsaved_changes:
            import inquirer
            questions = [
                inquirer.Confirm('confirm',
                               message='You have unsaved changes. Exit without saving?',
                               default=False)
            ]
            answers = inquirer.prompt(questions)
            if not answers or not answers['confirm']:
                return False
        
        show_info_message("Exiting without saving")
        return True
    
    def _handle_interrupt(self) -> bool:
        """Handle keyboard interrupt."""
        console.print()
        show_warning_message("Interrupted by user")
        return self._exit_without_saving()


def edit_yaml_config(file_path: Path, create_if_missing: bool = True) -> bool:
    """Main entry point for YAML configuration editing."""
    editor = InteractiveEditor(file_path)
    return editor.start() 