import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from .core.processor import PBIPProcessor
from .core.validator import validate_config, validate_data
from .utils.file_utils import read_yaml, read_csv
from .models.config import AppConfig
from .utils.logger import log_error, setup_logging

app = typer.Typer(help="Power BI Template Automation - Generate PBIP projects from templates")
console = Console()

@app.command()
def generate(
    template: str = typer.Option(..., "--template", "-t", help="Path to PBIP template folder"),
    config: str = typer.Option(..., "--config", "-c", help="Path to configuration file"),
    data: str = typer.Option(..., "--data", "-d", help="Path to CSV data file"),
    output_dir: str = typer.Option("./output", "--output-dir", "-o", help="Output directory for generated PBIP folders"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without generating files")
):
    """Generate PBIP projects from a template with parameter variations."""
    
    # Setup logging
    setup_logging(verbose=verbose)
    
    try:
        # Load and validate inputs
        template_path = Path(template)
        config_path = Path(config)
        data_path = Path(data)
        output_path = Path(output_dir)

        if not template_path.exists():
            log_error(f"Template folder not found: {template}")
            raise typer.Exit(1)

        if not config_path.exists():
            log_error(f"Config file not found: {config}")
            raise typer.Exit(1)

        if not data_path.exists():
            log_error(f"Data file not found: {data}")
            raise typer.Exit(1)

        # Load configuration and data
        config_data = read_yaml(config_path)
        app_config = AppConfig(**config_data)
        
        csv_data = read_csv(data_path)
        
        if verbose:
            console.print(f"[bold green]✓[/bold green] Loaded template: {template}")
            console.print(f"[bold green]✓[/bold green] Loaded config: {config}")
            console.print(f"[bold green]✓[/bold green] Loaded data: {len(csv_data)} rows")
            console.print(f"[bold green]✓[/bold green] Output directory: {output_dir}")

        # Validate configuration and data
        if not validate_config(config_data):
            log_error("Configuration validation failed")
            raise typer.Exit(1)

        if not validate_data(csv_data):
            log_error("Data validation failed")
            raise typer.Exit(1)

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Initialize processor
        processor = PBIPProcessor(template_path, config_data, output_path)

        if dry_run:
            console.print("\n[bold yellow]DRY RUN MODE[/bold yellow]")
            console.print("Preview of changes that would be made:")
            
            # Create parameter changes table
            table = Table(title="Parameter Changes Preview")
            table.add_column("Row", style="cyan")
            table.add_column("Parameter", style="magenta")
            table.add_column("New Value", style="green")
            
            for i, row in enumerate(csv_data, 1):
                summary = processor.get_parameter_summary(row)
                for param_name, param_info in summary.items():
                    table.add_row(str(i), param_name, str(param_info['value']))
            
            console.print(table)
            return

        # Process all rows
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating PBIP projects...", total=len(csv_data))
            
            generated_folders = processor.process_all(csv_data)
            
            progress.update(task, completed=len(csv_data))

        # Show results
        console.print(f"\n[bold green]✓[/bold green] Successfully generated {len(generated_folders)} PBIP projects in {output_dir}")
        
        if verbose:
            console.print("\n[bold]Generated folders:[/bold]")
            for folder in generated_folders:
                console.print(f"  • {folder.name}")

    except Exception as e:
        log_error(f"Generation failed: {e}")
        raise typer.Exit(1)

@app.command()
def validate(
    template: str = typer.Option(..., "--template", "-t", help="Path to PBIP template folder"),
    config: str = typer.Option(..., "--config", "-c", help="Path to configuration file"),
    data: str = typer.Option(..., "--data", "-d", help="Path to CSV data file")
):
    """Validate template, config, and data files."""
    
    try:
        # Load and validate inputs
        template_path = Path(template)
        config_path = Path(config)
        data_path = Path(data)

        if not template_path.exists():
            console.print(f"[bold red]✗[/bold red] Template folder not found: {template}")
            raise typer.Exit(1)

        if not config_path.exists():
            console.print(f"[bold red]✗[/bold red] Config file not found: {config}")
            raise typer.Exit(1)

        if not data_path.exists():
            console.print(f"[bold red]✗[/bold red] Data file not found: {data}")
            raise typer.Exit(1)

        # Load and validate configuration
        config_data = read_yaml(config_path)
        if validate_config(config_data):
            console.print("[bold green]✓[/bold green] Configuration is valid")
        else:
            console.print("[bold red]✗[/bold red] Configuration validation failed")
            raise typer.Exit(1)

        # Load and validate data
        csv_data = read_csv(data_path)
        if validate_data(csv_data):
            console.print("[bold green]✓[/bold green] Data is valid")
        else:
            console.print("[bold red]✗[/bold red] Data validation failed")
            raise typer.Exit(1)

        # Validate template structure
        try:
            # Check for required PBIP files
            pbip_file = template_path / f"{template_path.name}.pbip"
            if not pbip_file.exists():
                console.print(f"[bold red]✗[/bold red] PBIP file not found: {pbip_file}")
                raise typer.Exit(1)
            
            # Check for Report and SemanticModel folders
            report_folder = template_path / f"{template_path.name}.Report"
            semantic_model_folder = template_path / f"{template_path.name}.SemanticModel"
            
            if not report_folder.exists():
                console.print(f"[bold red]✗[/bold red] Report folder not found: {report_folder}")
                raise typer.Exit(1)
            
            if not semantic_model_folder.exists():
                console.print(f"[bold red]✗[/bold red] SemanticModel folder not found: {semantic_model_folder}")
                raise typer.Exit(1)
            
            # Check for model.bim file
            model_bim = semantic_model_folder / "model.bim"
            if not model_bim.exists():
                console.print(f"[bold red]✗[/bold red] model.bim file not found: {model_bim}")
                raise typer.Exit(1)
            
            console.print("[bold green]✓[/bold green] Template structure is valid")
            
        except Exception as e:
            console.print(f"[bold red]✗[/bold red] Template validation failed: {e}")
            raise typer.Exit(1)

        console.print("[bold green]✓[/bold green] All validations passed!")

    except Exception as e:
        log_error(f"Validation failed: {e}")
        raise typer.Exit(1)

@app.command()
def list_templates(
    templates_dir: str = typer.Option("./templates", "--templates-dir", help="Directory containing PBIP templates")
):
    """List available PBIP template folders."""
    
    try:
        templates_path = Path(templates_dir)
        
        if not templates_path.exists():
            console.print(f"[bold red]✗[/bold red] Templates directory not found: {templates_dir}")
            raise typer.Exit(1)

        # Find PBIP folders
        pbip_folders = []
        for item in templates_path.iterdir():
            if item.is_dir():
                pbip_file = item / f"{item.name}.pbip"
                if pbip_file.exists():
                    pbip_folders.append(item)

        if not pbip_folders:
            console.print(f"[yellow]No PBIP templates found in {templates_dir}[/yellow]")
            return

        # Create table
        table = Table(title="Available PBIP Templates")
        table.add_column("Template Name", style="cyan")
        table.add_column("Path", style="green")
        table.add_column("Status", style="magenta")

        for folder in pbip_folders:
            # Check if template is valid
            report_folder = folder / f"{folder.name}.Report"
            semantic_model_folder = folder / f"{folder.name}.SemanticModel"
            model_bim = semantic_model_folder / "model.bim" if semantic_model_folder.exists() else None
            
            if report_folder.exists() and semantic_model_folder.exists() and model_bim and model_bim.exists():
                status = "[green]Valid[/green]"
            else:
                status = "[red]Invalid[/red]"
            
            table.add_row(folder.name, str(folder), status)

        console.print(table)

    except Exception as e:
        log_error(f"Failed to list templates: {e}")
        raise typer.Exit(1)

@app.command()
def info():
    """Show information about the tool."""
    
    info_text = Text()
    info_text.append("Power BI Template Automation\n", style="bold blue")
    info_text.append("A sophisticated tool for programmatically generating modified Power BI project files\n\n", style="italic")
    
    info_text.append("Version: ", style="bold")
    info_text.append("0.1.0\n")
    info_text.append("Python: ", style="bold")
    info_text.append("3.9+\n")
    info_text.append("License: ", style="bold")
    info_text.append("MIT\n\n")
    
    info_text.append("Commands:\n", style="bold")
    info_text.append("  validate       Validate template, config, and data files\n")
    info_text.append("  list-templates List available template folders\n")
    info_text.append("  info          Show this information\n")
    
    panel = Panel(info_text, title="Power BI Template Automation", border_style="blue")
    console.print(panel)

def main():
    """Main entry point for the CLI application."""
    app()

if __name__ == "__main__":
    main() 