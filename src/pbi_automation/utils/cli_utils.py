from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text
from rich import print as rprint
import time

console = Console()

def show_splash_screen():
    """Display the ASCII art splash screen."""
    splash_art = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ██████╗ ██████╗ ██╗   ██╗██████╗  █████╗ ██╗               ║
    ║   ██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔══██╗██║               ║
    ║   ██████╔╝██████╔╝██║   ██║██████╔╝███████║██║               ║
    ║   ██╔═══╝ ██╔══██╗██║   ██║██╔═══╝ ██╔══██║██║               ║
    ║   ██║     ██████╔╝╚██████╔╝██║     ██║  ██║███████╗          ║
    ║   ╚═╝     ╚═════╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝╚══════╝          ║
    ║                                                              ║
    ║              [bold blue]PBIP-TEMPLATE-PAL[/bold blue]        ║
    ║              [dim]Generate PBIP projects with ease[/dim]     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    
    panel = Panel(
        splash_art,
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def show_success_message(message: str):
    """Display a success message with green styling."""
    console.print(f"[bold green]✓[/bold green] {message}")

def show_error_message(message: str):
    """Display an error message with red styling."""
    console.print(f"[bold red]✗[/bold red] {message}")

def show_warning_message(message: str):
    """Display a warning message with yellow styling."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")

def show_info_message(message: str):
    """Display an info message with blue styling."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")

def create_progress_bar(description: str = "Processing..."):
    """Create a progress bar with spinner."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )

def show_generated_folders(folders: list):
    """Display generated folders in a pretty table."""
    table = Table(title="[bold green]Generated PBIP Projects[/bold green]")
    table.add_column("Folder Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    
    for folder in folders:
        table.add_row(folder, "✓ Generated")
    
    console.print(table)

def show_config_summary(config_path: str, data_path: str, template_path: str, output_dir: str):
    """Display configuration summary in a panel."""
    summary = f"""
[bold]Configuration Summary[/bold]

[cyan]Template:[/cyan] {template_path}
[cyan]Config:[/cyan] {config_path}
[cyan]Data:[/cyan] {data_path}
[cyan]Output:[/cyan] {output_dir}
    """
    
    panel = Panel(summary, title="[bold blue]Setup Complete[/bold blue]", border_style="blue")
    console.print(panel)

def show_processing_header():
    """Display processing header with animation."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]🚀 Starting PBIP Generation[/bold blue]",
        border_style="blue"
    ))
    console.print()

def show_completion_message(success_count: int, total_count: int):
    """Display completion message with statistics."""
    console.print()
    panel = Panel(
        f"[bold green]🎉 Generation Complete![/bold green]\n\n"
        f"Successfully generated [bold green]{success_count}[/bold green] out of [bold]{total_count}[/bold] projects",
        title="[bold green]Success[/bold green]",
        border_style="green"
    )
    console.print(panel)

def show_interactive_header():
    """Display interactive mode header."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🎯 Interactive Mode[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

def show_help_menu():
    """Display help menu for interactive mode."""
    help_text = """
[bold]Available Commands:[/bold]

[cyan]generate[/cyan] - Start PBIP generation with interactive prompts
[cyan]edit[/cyan] - Edit YAML configuration file interactively
[cyan]version[/cyan] - Show version information
[cyan]help[/cyan] - Show this help menu
[cyan]exit[/cyan] - Exit the application
    """
    
    panel = Panel(help_text, title="[bold blue]Help Menu[/bold blue]", border_style="blue")
    console.print(panel)
    console.print() 