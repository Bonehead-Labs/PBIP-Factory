import click
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

app = typer.Typer()
console = Console()


@app.command()
def generate(
    template: str = typer.Option(..., "--template", "-t", help="Path to PBIP template folder"),
    config: str = typer.Option(..., "--config", "-c", help="Path to configuration YAML file"),
    data: str = typer.Option(..., "--data", "-d", help="Path to CSV data file"),
    output_dir: str = typer.Option("./output", "--output-dir", "-o", help="Output directory for generated projects"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Generate PBIP projects from template and data."""
    
    # Setup logging
    setup_logging(verbose=verbose)
    
    try:
        # Load configuration
        config_path = Path(config)
        if not config_path.exists():
            log_error(f"Configuration file not found: {config_path}")
            raise typer.Exit(1)
        
        app_config = Config.from_yaml(config_path)
        log_success(f"✓ Loaded config: {config}")
        
        # Load data
        data_path = Path(data)
        if not data_path.exists():
            log_error(f"Data file not found: {data_path}")
            raise typer.Exit(1)
        
        data_rows = load_data_from_csv(data_path)
        log_success(f"✓ Loaded data: {len(data_rows)} rows")
        
        # Validate template
        template_path = Path(template)
        if not template_path.exists():
            log_error(f"Template not found: {template_path}")
            raise typer.Exit(1)
        
        validator = PBIPValidator()
        if not validator.validate_template(template_path):
            log_error("Template validation failed")
            raise typer.Exit(1)
        
        log_success(f"✓ Validated PBIP template: {template}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        log_success(f"✓ Output directory: {output_dir}")
        
        # Process data
        processor = PBIPProcessor(app_config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating PBIP projects...", total=None)
            
            success_count = processor.process_data(template_path, data_rows, output_path)
            
            progress.update(task, completed=True)
        
        # Show results
        if success_count > 0:
            log_success(f"✓ Successfully generated {success_count} PBIP projects in {output_dir}")
            
            # List generated folders
            generated_folders = []
            for item in output_path.iterdir():
                if item.is_dir():
                    generated_folders.append(item.name)
            
            if generated_folders:
                console.print("\nGenerated folders:")
                for folder in sorted(generated_folders):
                    console.print(f"  • {folder}")
        
        else:
            log_error("No projects were generated successfully")
            raise typer.Exit(1)
            
    except Exception as e:
        log_error(f"Generation failed: {str(e)}")
        raise typer.Exit(1)


@app.command()
def validate(
    template: str = typer.Option(..., "--template", "-t", help="Path to PBIP template folder"),
    config: str = typer.Option(..., "--config", "-c", help="Path to configuration YAML file"),
    data: str = typer.Option(..., "--data", "-d", help="Path to CSV data file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Validate template, configuration, and data files."""
    
    # Setup logging
    setup_logging(verbose=verbose)
    
    try:
        # Validate template
        template_path = Path(template)
        if not template_path.exists():
            log_error(f"Template not found: {template_path}")
            raise typer.Exit(1)
        
        validator = PBIPValidator()
        if not validator.validate_template(template_path):
            log_error("Template validation failed")
            raise typer.Exit(1)
        
        log_success(f"✓ Template validation passed: {template}")
        
        # Validate configuration
        config_path = Path(config)
        if not config_path.exists():
            log_error(f"Configuration file not found: {config_path}")
            raise typer.Exit(1)
        
        try:
            app_config = Config.from_yaml(config_path)
            log_success(f"✓ Configuration validation passed: {config}")
        except Exception as e:
            log_error(f"Configuration validation failed: {str(e)}")
            raise typer.Exit(1)
        
        # Validate data
        data_path = Path(data)
        if not data_path.exists():
            log_error(f"Data file not found: {data_path}")
            raise typer.Exit(1)
        
        try:
            data_rows = load_data_from_csv(data_path)
            log_success(f"✓ Data validation passed: {len(data_rows)} rows")
        except Exception as e:
            log_error(f"Data validation failed: {str(e)}")
            raise typer.Exit(1)
        
        # Validate parameter mapping
        config_params = {param.name for param in app_config.parameters}
        if data_rows:
            data_columns = set(data_rows[0].data.keys())
            missing_params = config_params - data_columns
            extra_columns = data_columns - config_params
            
            if missing_params:
                log_error(f"Missing parameters in data: {missing_params}")
                raise typer.Exit(1)
            
            if extra_columns:
                log_warning(f"Extra columns in data (will be ignored): {extra_columns}")
            
            log_success("✓ Parameter mapping validation passed")
        
        log_success("✓ All validations passed!")
        
    except Exception as e:
        log_error(f"Validation failed: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 