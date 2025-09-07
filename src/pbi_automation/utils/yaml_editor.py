"""
YAML Configuration Editor for PBIP Factory.

Provides an interactive editor for YAML configuration files with validation,
automatic backups, and user-friendly menus.
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
    """Manage YAML files with validation and timestamped backup support."""
    
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.backup_path = self.file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        self._data: Optional[CommentedMap] = None
    
    def load(self) -> bool:
        """Load YAML file into memory with basic error handling."""
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
        """Persist YAML to disk, optionally creating a timestamped backup first."""
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
        """Return the in-memory YAML data structure (creates one if absent)."""
        if self._data is None:
            self._data = CommentedMap()
        return self._data
    
    def set_data(self, data: CommentedMap) -> None:
        """Replace the in-memory YAML data structure."""
        self._data = data
    
    def validate_structure(self) -> bool:
        """Validate the YAML shape: requires a list of parameter objects."""
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
            ('file', 'pbip_factory.log')
        ])
        
        # Add comments describing purpose
        default_config.yaml_add_eol_comment('Configuration for PBIP Factory parameter automation', 0)
        default_config.yaml_add_eol_comment('Maps CSV columns to model parameters (BIM/TMDL)', 0)
        
        return default_config


class InteractiveEditor:
    """Interactive YAML configuration editor with simple menus and prompts."""
    
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
        import inquirer
        
        questions = [
            inquirer.Confirm('create_new',
                           message=f'Configuration file not found. Create new file at {self.file_manager.file_path}?',
                           default=True)
        ]
        
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
        while True:
            try:
                choice = self._show_parameter_menu()
                
                if choice == '1':
                    self._list_parameters()
                elif choice == '2':
                    self._add_parameter()
                elif choice == '3':
                    self._edit_parameter()
                elif choice == '4':
                    self._delete_parameter()
                elif choice == '5':
                    break  # Return to main menu
                else:
                    show_error_message("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                show_error_message(f"An error occurred: {e}")
                log_error(f"Parameter editor error: {e}")
    
    def _show_parameter_menu(self) -> str:
        """Display the parameter editing menu."""
        console.print()
        console.print("┌─ Parameter Editor ──────────────────────────────┐")
        console.print("│                                                  │")
        console.print("│  What would you like to do?                     │")
        console.print("│                                                  │")
        console.print("│  [1] List Parameters                            │")
        console.print("│  [2] Add Parameter                              │")
        console.print("│  [3] Edit Parameter                             │")
        console.print("│  [4] Delete Parameter                           │")
        console.print("│  [5] Back to Main Menu                          │")
        console.print("│                                                  │")
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
        
        import inquirer
        questions = [
            inquirer.List('choice',
                         message='Select an option',
                         choices=['1', '2', '3', '4', '5'])
        ]
        
        answers = inquirer.prompt(questions)
        return answers['choice'] if answers else '5'
    
    def _list_parameters(self) -> None:
        """List all parameters in a formatted table."""
        data = self.file_manager.get_data()
        parameters = data.get('parameters', [])
        
        if not parameters:
            show_info_message("No parameters defined yet.")
            return
        
        console.print()
        console.print("┌─ Current Parameters ────────────────────────────┐")
        
        for i, param in enumerate(parameters, 1):
            name = param.get('name', 'Unknown')
            param_type = param.get('type', 'Unknown')
            console.print(f"│  {i:2d}. {name:<20} ({param_type})")
        
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
    
    def _add_parameter(self) -> None:
        """Add a new parameter."""
        import inquirer
        
        questions = [
            inquirer.Text('name',
                         message='Enter parameter name',
                         validate=lambda _, x: len(x.strip()) > 0 or 'Name cannot be empty'),
            inquirer.List('type',
                         message='Select parameter type',
                         choices=['string', 'integer', 'float', 'boolean'])
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        name = answers['name'].strip()
        param_type = answers['type']
        
        # Check if parameter already exists
        data = self.file_manager.get_data()
        parameters = data.get('parameters', [])
        
        for param in parameters:
            if param.get('name') == name:
                show_error_message(f"Parameter '{name}' already exists")
                return
        
        # Add new parameter
        new_param = CommentedMap([('name', name), ('type', param_type)])
        parameters.append(new_param)
        data['parameters'] = parameters
        
        self.unsaved_changes = True
        show_success_message(f"Added parameter '{name}' ({param_type})")
    
    def _edit_parameter(self) -> None:
        """Edit an existing parameter."""
        data = self.file_manager.get_data()
        parameters = data.get('parameters', [])
        
        if not parameters:
            show_info_message("No parameters to edit.")
            return
        
        # Show parameter list for selection
        console.print()
        console.print("┌─ Select Parameter to Edit ──────────────────────┐")
        
        for i, param in enumerate(parameters, 1):
            name = param.get('name', 'Unknown')
            param_type = param.get('type', 'Unknown')
            console.print(f"│  {i:2d}. {name:<20} ({param_type})")
        
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
        
        import inquirer
        questions = [
            inquirer.List('index',
                         message='Select parameter to edit',
                         choices=[str(i) for i in range(1, len(parameters) + 1)])
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        try:
            index = int(answers['index']) - 1
            param = parameters[index]
        except (ValueError, IndexError):
            show_error_message("Invalid parameter selection")
            return
        
        # Edit the parameter
        self._edit_single_parameter(param, index)
    
    def _edit_single_parameter(self, param: CommentedMap, index: int) -> None:
        """Edit a single parameter's properties."""
        import inquirer
        
        current_name = param.get('name', '')
        current_type = param.get('type', '')
        
        questions = [
            inquirer.Text('name',
                         message='Enter parameter name',
                         default=current_name,
                         validate=lambda _, x: len(x.strip()) > 0 or 'Name cannot be empty'),
            inquirer.List('type',
                         message='Select parameter type',
                         default=current_type,
                         choices=['string', 'integer', 'float', 'boolean'])
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        new_name = answers['name'].strip()
        new_type = answers['type']
        
        # Check if new name conflicts with other parameters
        data = self.file_manager.get_data()
        parameters = data.get('parameters', [])
        
        for i, other_param in enumerate(parameters):
            if i != index and other_param.get('name') == new_name:
                show_error_message(f"Parameter '{new_name}' already exists")
                return
        
        # Update the parameter
        param['name'] = new_name
        param['type'] = new_type
        
        self.unsaved_changes = True
        show_success_message(f"Updated parameter '{current_name}' to '{new_name}' ({new_type})")
    
    def _delete_parameter(self) -> None:
        """Delete a parameter."""
        data = self.file_manager.get_data()
        parameters = data.get('parameters', [])
        
        if not parameters:
            show_info_message("No parameters to delete.")
            return
        
        # Show parameter list for selection
        console.print()
        console.print("┌─ Select Parameter to Delete ────────────────────┐")
        
        for i, param in enumerate(parameters, 1):
            name = param.get('name', 'Unknown')
            param_type = param.get('type', 'Unknown')
            console.print(f"│  {i:2d}. {name:<20} ({param_type})")
        
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
        
        import inquirer
        questions = [
            inquirer.List('index',
                         message='Select parameter to delete',
                         choices=[str(i) for i in range(1, len(parameters) + 1)]),
            inquirer.Confirm('confirm',
                           message='Are you sure you want to delete this parameter?',
                           default=False)
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or not answers['confirm']:
            return
        
        try:
            index = int(answers['index']) - 1
            deleted_param = parameters.pop(index)
            deleted_name = deleted_param.get('name', 'Unknown')
            
            self.unsaved_changes = True
            show_success_message(f"Deleted parameter '{deleted_name}'")
            
        except (ValueError, IndexError):
            show_error_message("Invalid parameter selection")
    
    def _edit_output_settings(self) -> None:
        """Edit output settings."""
        while True:
            try:
                choice = self._show_output_menu()
                
                if choice == '1':
                    self._edit_output_directory()
                elif choice == '2':
                    self._view_output_settings()
                elif choice == '3':
                    break  # Return to main menu
                else:
                    show_error_message("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                show_error_message(f"An error occurred: {e}")
                log_error(f"Output settings editor error: {e}")
    
    def _show_output_menu(self) -> str:
        """Display the output settings menu."""
        console.print()
        console.print("┌─ Output Settings Editor ───────────────────────┐")
        console.print("│                                                  │")
        console.print("│  What would you like to do?                     │")
        console.print("│                                                  │")
        console.print("│  [1] Edit Output Directory                      │")
        console.print("│  [2] View Current Settings                      │")
        console.print("│  [3] Back to Main Menu                          │")
        console.print("│                                                  │")
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
        
        import inquirer
        questions = [
            inquirer.List('choice',
                         message='Select an option',
                         choices=['1', '2', '3'])
        ]
        
        answers = inquirer.prompt(questions)
        return answers['choice'] if answers else '3'
    
    def _edit_output_directory(self) -> None:
        """Edit the output directory setting."""
        data = self.file_manager.get_data()
        
        # Ensure output section exists
        if 'output' not in data:
            data['output'] = CommentedMap()
        
        current_directory = data['output'].get('directory', './output')
        
        import inquirer
        questions = [
            inquirer.Text('directory',
                         message='Enter output directory path',
                         default=current_directory)
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        new_directory = answers['directory'].strip()
        if not new_directory:
            show_error_message("Directory path cannot be empty")
            return
        
        # Update the setting
        data['output']['directory'] = new_directory
        
        self.unsaved_changes = True
        show_success_message(f"Updated output directory to: {new_directory}")
    
    def _view_output_settings(self) -> None:
        """View current output settings."""
        data = self.file_manager.get_data()
        output = data.get('output', {})
        
        console.print()
        console.print("┌─ Current Output Settings ──────────────────────┐")
        
        directory = output.get('directory', './output')
        console.print(f"│  Directory: {directory}")
        
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
    
    def _edit_logging_config(self) -> None:
        """Edit logging configuration."""
        while True:
            try:
                choice = self._show_logging_menu()
                
                if choice == '1':
                    self._edit_log_level()
                elif choice == '2':
                    self._edit_log_format()
                elif choice == '3':
                    self._edit_log_file()
                elif choice == '4':
                    self._view_logging_settings()
                elif choice == '5':
                    break  # Return to main menu
                else:
                    show_error_message("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                show_error_message(f"An error occurred: {e}")
                log_error(f"Logging editor error: {e}")
    
    def _show_logging_menu(self) -> str:
        """Display the logging configuration menu."""
        console.print()
        console.print("┌─ Logging Configuration Editor ─────────────────┐")
        console.print("│                                                  │")
        console.print("│  What would you like to do?                     │")
        console.print("│                                                  │")
        console.print("│  [1] Edit Log Level                             │")
        console.print("│  [2] Edit Log Format                            │")
        console.print("│  [3] Edit Log File                              │")
        console.print("│  [4] View Current Settings                      │")
        console.print("│  [5] Back to Main Menu                          │")
        console.print("│                                                  │")
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
        
        import inquirer
        questions = [
            inquirer.List('choice',
                         message='Select an option',
                         choices=['1', '2', '3', '4', '5'])
        ]
        
        answers = inquirer.prompt(questions)
        return answers['choice'] if answers else '5'
    
    def _edit_log_level(self) -> None:
        """Edit the log level setting."""
        data = self.file_manager.get_data()
        
        # Ensure logging section exists
        if 'logging' not in data:
            data['logging'] = CommentedMap()
        
        current_level = data['logging'].get('level', 'INFO')
        
        import inquirer
        questions = [
            inquirer.List('level',
                         message='Select log level',
                         default=current_level,
                         choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        new_level = answers['level']
        
        # Update the setting
        data['logging']['level'] = new_level
        
        self.unsaved_changes = True
        show_success_message(f"Updated log level to: {new_level}")
    
    def _edit_log_format(self) -> None:
        """Edit the log format setting."""
        data = self.file_manager.get_data()
        
        # Ensure logging section exists
        if 'logging' not in data:
            data['logging'] = CommentedMap()
        
        current_format = data['logging'].get('format', 'json')
        
        import inquirer
        questions = [
            inquirer.List('format',
                         message='Select log format',
                         default=current_format,
                         choices=['json', 'text'])
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        new_format = answers['format']
        
        # Update the setting
        data['logging']['format'] = new_format
        
        self.unsaved_changes = True
        show_success_message(f"Updated log format to: {new_format}")
    
    def _edit_log_file(self) -> None:
        """Edit the log file setting."""
        data = self.file_manager.get_data()
        
        # Ensure logging section exists
        if 'logging' not in data:
            data['logging'] = CommentedMap()
        
        current_file = data['logging'].get('file', 'pbi_automation.log')
        
        import inquirer
        questions = [
            inquirer.Text('file',
                         message='Enter log file path (or leave empty to disable file logging)',
                         default=current_file)
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        new_file = answers['file'].strip()
        
        # Update the setting
        if new_file:
            data['logging']['file'] = new_file
            show_success_message(f"Updated log file to: {new_file}")
        else:
            # Remove file setting to disable file logging
            if 'file' in data['logging']:
                del data['logging']['file']
            show_success_message("Disabled file logging")
        
        self.unsaved_changes = True
    
    def _view_logging_settings(self) -> None:
        """View current logging settings."""
        data = self.file_manager.get_data()
        logging = data.get('logging', {})
        
        console.print()
        console.print("┌─ Current Logging Settings ─────────────────────┐")
        
        level = logging.get('level', 'INFO')
        format_type = logging.get('format', 'json')
        log_file = logging.get('file', 'pbi_automation.log')
        
        console.print(f"│  Level:  {level}")
        console.print(f"│  Format: {format_type}")
        console.print(f"│  File:   {log_file}")
        
        console.print("└──────────────────────────────────────────────────┘")
        console.print()
    
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