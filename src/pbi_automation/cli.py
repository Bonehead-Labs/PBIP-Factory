import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import inquirer
from typing import Optional

from .core.processor import PBIPProcessor
from .core.validator import PBIPValidator
from .models.config import Config
from .models.data import load_data_from_csv
from .utils.logger import setup_logging, log_info, log_error, log_success
from .utils.cli_utils import (
    show_splash_screen, show_success_message, show_error_message, 
    show_warning_message, show_info_message, create_progress_bar,
    show_generated_folders, show_config_summary, show_processing_header,
    show_completion_message, show_interactive_header, show_help_menu
)
from .utils.yaml_editor import edit_yaml_config
from .utils.tmdl_parser import TMDLParser
from .utils.discovery import DiscoveryManager

app = typer.Typer(name="pbip-template-pal", help="PBIP Template Automation Tool")
console = Console()


def prompt_for_template() -> str:
    """Prompt user for template path and validate it exists."""
    while True:
        questions = [
            inquirer.Text('template', 
                         message='Enter the path to your PBIP template folder',
                         default='Example_PBIP')
        ]
        answers = inquirer.prompt(questions)
        path = answers['template']
        if Path(path).exists() and Path(path).is_dir():
            return path
        else:
            show_error_message(f"Template folder not found: {path}")


def prompt_for_config() -> str:
    """Prompt user for config path and validate it exists."""
    while True:
        questions = [
            inquirer.Text('config', 
                         message='Enter the path to your configuration YAML file',
                         default='examples/configs/pbip_config.yaml')
        ]
        answers = inquirer.prompt(questions)
        path = answers['config']
        if Path(path).exists() and Path(path).is_file():
            return path
        else:
            show_error_message(f"Configuration file not found: {path}")


def prompt_for_data() -> str:
    """Prompt user for data path and validate it exists."""
    while True:
        questions = [
            inquirer.Text('data', 
                         message='Enter the path to your CSV data file',
                         default='examples/data/pbip_data.csv')
        ]
        answers = inquirer.prompt(questions)
        path = answers['data']
        if Path(path).exists() and Path(path).is_file():
            return path
        else:
            show_error_message(f"Data file not found: {path}")


def prompt_for_output() -> str:
    """Prompt user for output directory (create if not exists)."""
    while True:
        questions = [
            inquirer.Text('output', 
                         message='Enter the output directory for generated projects',
                         default='output')
        ]
        answers = inquirer.prompt(questions)
        path = answers['output']
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return path
        except Exception as e:
            show_error_message(f"Failed to create output directory: {e}")


def prompt_for_verbose() -> bool:
    """Prompt user for verbose mode."""
    questions = [
        inquirer.Confirm('verbose', 
                        message='Enable verbose logging?',
                        default=False)
    ]
    answers = inquirer.prompt(questions)
    return answers['verbose']


def run_interactive_selection(discovery: DiscoveryManager) -> tuple[str, str, str, str]:
    """Run interactive selection for template, config, data, and output, with manual entry option."""
    # Select template
    templates = discovery.get_available_templates()
    if not templates:
        show_error_message("No templates found. Please add templates to the templates/ directory.")
        return None, None, None, None

    template_choices = [f"{t['name']} ({t['type']})" for t in templates]
    template_choices.append("Other (type manually)")
    questions = [
        inquirer.List('template',
                     message='Select a template:',
                     choices=template_choices)
    ]
    answers = inquirer.prompt(questions)
    if answers['template'] == "Other (type manually)":
        manual = inquirer.prompt([
            inquirer.Text('manual_template', message='Enter the path to your PBIP template folder')
        ])
        template_path = manual['manual_template']
    else:
        selected_template = templates[template_choices.index(answers['template'])]
        template_path = selected_template['path']

    # Select config
    configs = discovery.get_available_configs()
    if not configs:
        show_error_message("No configuration files found. Please add configs to the configs/ directory.")
        return None, None, None, None

    config_choices = [f"{c['name']} ({c['type']})" for c in configs]
    config_choices.append("Other (type manually)")
    questions = [
        inquirer.List('config',
                     message='Select a configuration file:',
                     choices=config_choices)
    ]
    answers = inquirer.prompt(questions)
    if answers['config'] == "Other (type manually)":
        manual = inquirer.prompt([
            inquirer.Text('manual_config', message='Enter the path to your configuration YAML file')
        ])
        config_path = manual['manual_config']
    else:
        selected_config = configs[config_choices.index(answers['config'])]
        config_path = selected_config['path']

    # Select data
    data_files = discovery.get_available_data_files()
    if not data_files:
        show_error_message("No data files found. Please add CSV files to the data/ directory.")
        return None, None, None, None

    data_choices = [f"{d['name']} ({d['type']})" for d in data_files]
    data_choices.append("Other (type manually)")
    questions = [
        inquirer.List('data',
                     message='Select a data file:',
                     choices=data_choices)
    ]
    answers = inquirer.prompt(questions)
    if answers['data'] == "Other (type manually)":
        manual = inquirer.prompt([
            inquirer.Text('manual_data', message='Enter the path to your CSV data file')
        ])
        data_path = manual['manual_data']
    else:
        selected_data = data_files[data_choices.index(answers['data'])]
        data_path = selected_data['path']

    # Get output directory
    if isinstance(template_path, str) and Path(template_path).exists():
        template_name = Path(template_path).name
    else:
        template_name = "output"
    output_path = discovery.get_output_path(template_name)

    return template_path, config_path, data_path, str(output_path)


def resolve_template_path(template: str, discovery: DiscoveryManager) -> Optional[str]:
    """Resolve template name to path."""
    if Path(template).exists():
        return template
    
    template_path = discovery.get_template_path(template)
    if template_path:
        return str(template_path)
    
    show_error_message(f"Template not found: {template}")
    return None


def resolve_config_path(config: str, discovery: DiscoveryManager) -> Optional[str]:
    """Resolve config name to path."""
    if Path(config).exists():
        return config
    
    config_path = discovery.get_config_path(config)
    if config_path:
        return str(config_path)
    
    show_error_message(f"Configuration file not found: {config}")
    return None


def resolve_data_path(data: str, discovery: DiscoveryManager) -> Optional[str]:
    """Resolve data name to path."""
    if Path(data).exists():
        return data
    
    data_path = discovery.get_data_path(data)
    if data_path:
        return str(data_path)
    
    show_error_message(f"Data file not found: {data}")
    return None


def resolve_output_path(template_path: str, output_dir: Optional[str], discovery: DiscoveryManager) -> str:
    """Resolve output directory."""
    if output_dir:
        return output_dir
    
    template_name = Path(template_path).name
    return str(discovery.get_output_path(template_name))


def run_generation(template: str, config: str, data: str, output_dir: str, verbose: bool = False):
    """Run the PBIP generation process."""
    try:
        setup_logging(verbose=verbose)
        config_path = Path(config)
        if not config_path.exists():
            show_error_message(f"Configuration file not found: {config}")
            return False
        try:
            config_obj = Config.from_yaml(config_path)
        except Exception as e:
            show_error_message(f"Failed to load configuration: {e}")
            return False
        show_success_message(f"Loaded config: {config}")
        data_path = Path(data)
        if not data_path.exists():
            show_error_message(f"Data file not found: {data}")
            return False
        try:
            data_rows = load_data_from_csv(data_path)
        except Exception as e:
            show_error_message(f"Failed to load data: {e}")
            return False
        show_success_message(f"Loaded data: {len(data_rows)} rows")
        template_path = Path(template)
        if not template_path.exists():
            show_error_message(f"Template not found: {template}")
            return False
        validator = PBIPValidator()
        if not validator.validate_template(template_path):
            show_error_message(f"Invalid template: {template}")
            return False
        show_success_message(f"Validated PBIP template: {template}")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        show_success_message(f"Output directory: {output_dir}")
        show_config_summary(config, data, template, output_dir)
        show_processing_header()
        processor = PBIPProcessor(config_obj)
        with create_progress_bar("Generating PBIP projects...") as progress:
            task = progress.add_task("Processing...", total=len(data_rows))
            success_count = processor.process_data(template_path, data_rows, output_path)
            progress.update(task, completed=len(data_rows))
        show_completion_message(success_count, len(data_rows))
        generated_folders = [row.get_folder_name() for row in data_rows]
        show_generated_folders(generated_folders)
        log_success(f"Successfully generated {success_count} PBIP projects in {output_dir}")
        # --- Summary report ---
        failed_count = len(data_rows) - success_count
        if failed_count > 0:
            show_warning_message(f"{failed_count} project(s) failed to generate. See errors above.")
        else:
            show_success_message("All projects generated successfully!")
        return True
    except (OSError, ValueError) as e:
        show_error_message(f"A file or data error occurred: {str(e)}")
        if verbose:
            console.print_exception()
        return False
    except Exception as e:
        show_error_message(f"An unexpected error occurred: {str(e)}")
        if verbose:
            console.print_exception()
        raise


def run_detection(template: str, verbose: bool = False):
    """Run the template detection process."""
    try:
        setup_logging(verbose=verbose)
        
        template_path = Path(template)
        if not template_path.exists():
            show_error_message(f"Template not found: {template}")
            return False
        
        if not template_path.is_dir():
            show_error_message(f"Template path must be a directory: {template}")
            return False
        
        # Validate the template structure
        validator = PBIPValidator()
        if not validator.validate_template(template_path):
            show_error_message(f"Invalid template: {template}")
            return False
        
        # Detect model format
        template_name = template_path.name
        semantic_model_folder = template_path / f"{template_name}.SemanticModel"
        tmdl_parser = TMDLParser()
        model_format = tmdl_parser.detect_model_format(semantic_model_folder)
        
        # Display results
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]Template Analysis Results[/bold cyan]\n"
            f"[bold]Template:[/bold] {template}\n"
            f"[bold]Model Format:[/bold] {model_format.upper()}",
            title="🔍 Template Detection",
            border_style="cyan"
        ))
        
        # Display parameters if found
        if model_format == "bim":
            # For BIM format, we need to parse the model.bim file
            model_bim_path = semantic_model_folder / "model.bim"
            if model_bim_path.exists():
                import json
                with open(model_bim_path, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                
                model = model_data.get("model", {})
                expressions = model.get("expressions", [])
                
                if expressions:
                    table = Table(title="📋 Parameters Found (BIM Format)")
                    table.add_column("Parameter Name", style="cyan", no_wrap=True)
                    table.add_column("Current Value", style="green")
                    table.add_column("Type", style="yellow")
                    
                    for expression in expressions:
                        param_name = expression.get("name", "")
                        expression_text = expression.get("expression", "")
                        
                        # Extract value from expression
                        import re
                        value_match = re.search(r'"([^"]+)"', expression_text)
                        current_value = value_match.group(1) if value_match else "Unknown"
                        
                        table.add_row(param_name, current_value, "Parameter")
                    
                    console.print(table)
                else:
                    show_warning_message("No parameters found in BIM model")
        
        elif model_format == "tmdl":
            # For TMDL format, use the TMDL parser
            parameters = tmdl_parser.get_all_parameters(semantic_model_folder)
            
            if parameters:
                table = Table(title="📋 Parameters Found (TMDL Format)")
                table.add_column("Parameter Name", style="cyan", no_wrap=True)
                table.add_column("Current Value", style="green")
                table.add_column("Type", style="yellow")
                
                for param_name, current_value in parameters.items():
                    table.add_row(param_name, current_value, "Parameter")
                
                console.print(table)
            else:
                show_warning_message("No parameters found in TMDL model")
        
        show_success_message(f"Template analysis completed successfully!")
        return True
        
    except (OSError, ValueError) as e:
        show_error_message(f"A file or data error occurred: {str(e)}")
        if verbose:
            console.print_exception()
        return False
    except Exception as e:
        show_error_message(f"An unexpected error occurred: {str(e)}")
        if verbose:
            console.print_exception()
        raise


@app.command()
def generate(
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Template name or path"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config name or path"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Data file name or path"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Use interactive selection")
):
    """Generate PBIP projects from template with parameter updates."""
    
    # Show splash screen
    show_splash_screen()
    
    discovery = DiscoveryManager()
    
    # If no arguments provided, use interactive mode
    if not any([template, config, data]) or interactive:
        template, config, data, output_dir = run_interactive_selection(discovery)
    else:
        # Resolve names to paths
        template = resolve_template_path(template, discovery)
        config = resolve_config_path(config, discovery)
        data = resolve_data_path(data, discovery)
        output_dir = resolve_output_path(template, output_dir, discovery)
    
    if not all([template, config, data]):
        show_error_message("Missing required parameters. Use --interactive for guided selection.")
        raise typer.Exit(1)
    
    success = run_generation(template, config, data, output_dir, verbose)
    
    if not success:
        raise typer.Exit(1)


@app.command()
def list(
    item_type: str = typer.Argument(..., help="Type of items to list: templates, configs, data")
):
    """List available templates, configs, or data files."""
    discovery = DiscoveryManager()
    
    if item_type.lower() == "templates":
        templates = discovery.get_available_templates()
        console.print(discovery.format_template_list(templates))
    elif item_type.lower() == "configs":
        configs = discovery.get_available_configs()
        console.print(discovery.format_config_list(configs))
    elif item_type.lower() == "data":
        data_files = discovery.get_available_data_files()
        console.print(discovery.format_data_list(data_files))
    else:
        show_error_message(f"Unknown item type: {item_type}. Use: templates, configs, or data")
        raise typer.Exit(1)


@app.command()
def launch():
    """Launch PBIP-TEMPLATE-PAL in interactive mode."""
    show_splash_screen()
    show_interactive_header()
    show_help_menu()
    discovery = DiscoveryManager()
    
    while True:
        try:
            questions = [
                inquirer.List('command',
                            message='What would you like to do?',
                            choices=['generate', 'detect', 'edit', 'version', 'help', 'exit'])
            ]
            answers = inquirer.prompt(questions)
            
            if not answers:
                continue
                
            command = answers['command']
            
            if command == 'exit':
                console.print("[bold green]Goodbye! 👋[/bold green]")
                break
                
            elif command == 'version':
                console.print("[bold blue]Version:[/bold blue] 1.0.0")
                console.print("[bold blue]PBIP-TEMPLATE-PAL[/bold blue]")
                console.print()
                
            elif command == 'help':
                show_help_menu()
                
            elif command == 'detect':
                console.print()
                console.print("[bold cyan]Let's analyze your PBIP template! 🔍[/bold cyan]")
                console.print()
                
                # Prompt for template path
                template = prompt_for_template()
                verbose = prompt_for_verbose()
                
                if template:
                    console.print()
                    success = run_detection(template, verbose)
                    
                    if success:
                        console.print()
                        console.print("[bold green]Template analysis completed successfully! 🎉[/bold green]")
                    else:
                        console.print()
                        console.print("[bold red]Template analysis failed. Please check the errors above.[/bold red]")
                else:
                    show_error_message("Template path is required. Please try again.")
                
                console.print()
                show_help_menu()
                
            elif command == 'edit':
                console.print()
                console.print("[bold cyan]Let's edit your configuration! ⚙️[/bold cyan]")
                console.print()
                
                # Prompt for config file
                config = prompt_for_config()
                
                if config:
                    console.print()
                    success = edit_yaml_config(Path(config), create_if_missing=True)
                    
                    if success:
                        console.print()
                        console.print("[bold green]Configuration editing completed! 🎉[/bold green]")
                    else:
                        console.print()
                        console.print("[bold red]Configuration editing failed. Please check the errors above.[/bold red]")
                else:
                    show_error_message("Configuration file path is required. Please try again.")
                
                console.print()
                show_help_menu()
                
            elif command == 'generate':
                console.print()
                console.print("[bold cyan]Let's generate some PBIP projects! 🚀[/bold cyan]")
                console.print()
                
                # Use new interactive selection for template/config/data
                template, config, data, output_dir = run_interactive_selection(discovery)
                verbose = prompt_for_verbose()
                
                if all([template, config, data, output_dir]):
                    console.print()
                    success = run_generation(template, config, data, output_dir, verbose)
                    
                    if success:
                        console.print()
                        console.print("[bold green]Generation completed successfully! 🎉[/bold green]")
                    else:
                        console.print()
                        console.print("[bold red]Generation failed. Please check the errors above.[/bold red]")
                else:
                    show_error_message("All arguments are required. Please try again.")
                
                console.print()
                show_help_menu()
                
        except KeyboardInterrupt:
            console.print("\n[bold green]Goodbye! 👋[/bold green]")
            break
        except Exception as e:
            show_error_message(f"An error occurred: {str(e)}")
            console.print()


@app.command()
def edit(
    config: str = typer.Option("examples/configs/pbip_config.yaml", "--config", "-c", help="Path to configuration YAML file to edit"),
    create: bool = typer.Option(False, "--create", help="Create new configuration file if it doesn't exist")
):
    """Edit YAML configuration file interactively."""
    
    # Show splash screen
    show_splash_screen()
    
    config_path = Path(config)
    
    # Check if file exists
    if not config_path.exists() and not create:
        show_error_message(f"Configuration file not found: {config}")
        show_info_message("Use --create flag to create a new configuration file")
        raise typer.Exit(1)
    
    # Start the interactive editor
    success = edit_yaml_config(config_path, create_if_missing=create)
    
    if not success:
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    show_splash_screen()
    console.print("[bold blue]Version:[/bold blue] 1.0.0")
    console.print("[bold blue]PBIP-TEMPLATE-PAL[/bold blue]")


@app.command()
def detect(
    template: str = typer.Option(..., "--template", "-t", help="Path to PBIP template folder"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Detect and display the model format and parameters of a PBIP template."""
    
    # Show splash screen
    show_splash_screen()
    
    try:
        setup_logging(verbose=verbose)
        
        template_path = Path(template)
        if not template_path.exists():
            show_error_message(f"Template not found: {template}")
            raise typer.Exit(1)
        
        if not template_path.is_dir():
            show_error_message(f"Template path must be a directory: {template}")
            raise typer.Exit(1)
        
        # Validate the template structure
        validator = PBIPValidator()
        if not validator.validate_template(template_path):
            show_error_message(f"Invalid template: {template}")
            raise typer.Exit(1)
        
        # Detect model format
        template_name = template_path.name
        semantic_model_folder = template_path / f"{template_name}.SemanticModel"
        tmdl_parser = TMDLParser()
        model_format = tmdl_parser.detect_model_format(semantic_model_folder)
        
        # Display results
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]Template Analysis Results[/bold cyan]\n"
            f"[bold]Template:[/bold] {template}\n"
            f"[bold]Model Format:[/bold] {model_format.upper()}",
            title="🔍 Template Detection",
            border_style="cyan"
        ))
        
        # Display parameters if found
        if model_format == "bim":
            # For BIM format, we need to parse the model.bim file
            model_bim_path = semantic_model_folder / "model.bim"
            if model_bim_path.exists():
                import json
                with open(model_bim_path, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                
                model = model_data.get("model", {})
                expressions = model.get("expressions", [])
                
                if expressions:
                    table = Table(title="📋 Parameters Found (BIM Format)")
                    table.add_column("Parameter Name", style="cyan", no_wrap=True)
                    table.add_column("Current Value", style="green")
                    table.add_column("Type", style="yellow")
                    
                    for expression in expressions:
                        param_name = expression.get("name", "")
                        expression_text = expression.get("expression", "")
                        
                        # Extract value from expression
                        import re
                        value_match = re.search(r'"([^"]+)"', expression_text)
                        current_value = value_match.group(1) if value_match else "Unknown"
                        
                        table.add_row(param_name, current_value, "Parameter")
                    
                    console.print(table)
                else:
                    show_warning_message("No parameters found in BIM model")
        
        elif model_format == "tmdl":
            # For TMDL format, use the TMDL parser
            parameters = tmdl_parser.get_all_parameters(semantic_model_folder)
            
            if parameters:
                table = Table(title="📋 Parameters Found (TMDL Format)")
                table.add_column("Parameter Name", style="cyan", no_wrap=True)
                table.add_column("Current Value", style="green")
                table.add_column("Type", style="yellow")
                
                for param_name, current_value in parameters.items():
                    table.add_row(param_name, current_value, "Parameter")
                
                console.print(table)
            else:
                show_warning_message("No parameters found in TMDL model")
        
        show_success_message(f"Template analysis completed successfully!")
        
    except (OSError, ValueError) as e:
        show_error_message(f"A file or data error occurred: {str(e)}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"An unexpected error occurred: {str(e)}")
        if verbose:
            console.print_exception()
        raise


def main():
    """Main entry point for the application."""
    app()


if __name__ == "__main__":
    main() 