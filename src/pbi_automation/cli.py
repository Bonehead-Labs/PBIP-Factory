import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from .core.processor import PBIPProcessor
from .core.validator import PBIPValidator
from .models.config import Config
from .models.data import load_data_from_csv
from .utils.logger import setup_logging, log_info, log_error, log_success
from .utils.cli_utils import (
    show_splash_screen, show_success_message, show_error_message, 
    show_warning_message, show_info_message, create_progress_bar,
    show_generated_folders, show_config_summary, show_processing_header,
    show_completion_message
)

app = typer.Typer()
console = Console()


@app.command()
def generate(
    template: str = typer.Option(..., "--template", "-t", help="Path to PBIP template folder"),
    config: str = typer.Option(..., "--config", "-c", help="Path to configuration YAML file"),
    data: str = typer.Option(..., "--data", "-d", help="Path to CSV data file"),
    output_dir: str = typer.Option(..., "--output-dir", "-o", help="Output directory for generated projects"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Generate PBIP projects from template with parameter updates."""
    
    # Show splash screen
    show_splash_screen()
    
    try:
        # Setup logging
        setup_logging(verbose=verbose)
        
        # Load configuration
        config_path = Path(config)
        if not config_path.exists():
            show_error_message(f"Configuration file not found: {config}")
            raise typer.Exit(1)
        
        config_obj = Config.from_yaml(config_path)
        show_success_message(f"Loaded config: {config}")
        
        # Load data
        data_path = Path(data)
        if not data_path.exists():
            show_error_message(f"Data file not found: {data}")
            raise typer.Exit(1)
        
        data_rows = load_data_from_csv(data_path)
        show_success_message(f"Loaded data: {len(data_rows)} rows")
        
        # Validate template
        template_path = Path(template)
        if not template_path.exists():
            show_error_message(f"Template not found: {template}")
            raise typer.Exit(1)
        
        validator = PBIPValidator()
        if not validator.validate_template(template_path):
            show_error_message(f"Invalid template: {template}")
            raise typer.Exit(1)
        
        show_success_message(f"Validated PBIP template: {template}")
        
        # Setup output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        show_success_message(f"Output directory: {output_dir}")
        
        # Show configuration summary
        show_config_summary(config, data, template, output_dir)
        
        # Show processing header
        show_processing_header()
        
        # Process data with progress bar
        processor = PBIPProcessor(config_obj)
        
        with create_progress_bar("Generating PBIP projects...") as progress:
            task = progress.add_task("Processing...", total=len(data_rows))
            
            success_count = processor.process_data(template_path, data_rows, output_path)
            
            progress.update(task, completed=len(data_rows))
        
        # Show completion message
        show_completion_message(success_count, len(data_rows))
        
        # Show generated folders
        generated_folders = [row.get_folder_name() for row in data_rows]
        show_generated_folders(generated_folders)
        
        log_success(f"Successfully generated {success_count} PBIP projects in {output_dir}")
        
    except Exception as e:
        show_error_message(f"An error occurred: {str(e)}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    show_splash_screen()
    console.print("[bold blue]Version:[/bold blue] 1.0.0")
    console.print("[bold blue]Power BI Template Automation Tool[/bold blue]")


if __name__ == "__main__":
    app() 