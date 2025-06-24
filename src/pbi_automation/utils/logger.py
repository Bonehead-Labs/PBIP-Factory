import structlog
from rich.console import Console
import logging

console = Console()

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def log_info(message: str):
    logger.info(message)
    console.print(f"[green][INFO][/green] {message}")

def log_error(message: str):
    logger.error(message)
    console.print(f"[red][ERROR][/red] {message}")

def setup_logging(verbose: bool = False, level: str = "INFO"):
    """Setup logging level and format."""
    log_level = logging.DEBUG if verbose else getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=log_level) 