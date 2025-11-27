"""
Logging configuration and setup with color support.
"""
import logging
import sys
from app.core.config_settings import settings
from app.utils.color_log import Colors, _supports_color


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for different log levels."""
    
    # Color mapping for log levels
    LEVEL_COLORS = {
        "DEBUG": Colors.BRIGHT_BLACK,
        "INFO": Colors.BRIGHT_CYAN,
        "WARNING": Colors.BRIGHT_YELLOW,
        "ERROR": Colors.BRIGHT_RED,
        "CRITICAL": Colors.BRIGHT_RED + Colors.BOLD,
    }
    
    # Color for logger name
    NAME_COLOR = Colors.BRIGHT_MAGENTA
    
    def __init__(self, use_color: bool = True):
        """
        Initialize formatter.
        
        Args:
            use_color: Whether to use colors (auto-detected if None)
        """
        self.use_color = use_color if use_color is not None else _supports_color()
        
        if self.use_color:
            fmt = (
                f"{Colors.BRIGHT_BLACK}%(asctime)s{Colors.RESET} | "
                f"{Colors.BRIGHT_MAGENTA}%(name)s{Colors.RESET} | "
                f"%(levelname)s | "
                f"%(message)s"
            )
        else:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if self.use_color:
            # Colorize level name
            level_color = self.LEVEL_COLORS.get(record.levelname, Colors.WHITE)
            record.levelname = f"{level_color}{Colors.BOLD}{record.levelname}{Colors.RESET}"
            
            # Colorize logger name (shorten if too long)
            name = record.name
            if len(name) > 30:
                # Keep last part of module path
                parts = name.split(".")
                name = "..." + ".".join(parts[-2:])
            record.name = f"{self.NAME_COLOR}{name}{Colors.RESET}"
        
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with color support.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    handler = logging.StreamHandler(sys.stdout)
    
    # Use colored formatter for development, JSON for production
    if settings.ENVIRONMENT == "production":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Use colored formatter for development
        formatter = ColoredFormatter(use_color=True)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger








