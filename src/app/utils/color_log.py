"""
Color logging utilities for better log visibility.

Provides colored log formatting for different log levels and message types.
"""
from typing import Optional
import sys


class Colors:
    """ANSI color codes for terminal output."""
    
    # Reset
    RESET = "\033[0m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"


def colorize(text: str, color: str, bold: bool = False) -> str:
    """
    Add color to text.
    
    Args:
        text: Text to colorize
        color: Color code (from Colors class)
        bold: Whether to make text bold
        
    Returns:
        Colorized text string
    """
    if not _supports_color():
        return text
    
    style = Colors.BOLD if bold else ""
    return f"{style}{color}{text}{Colors.RESET}"


def _supports_color() -> bool:
    """Check if terminal supports color output."""
    # Check if running in a terminal
    if not sys.stdout.isatty():
        return False
    
    # Check for NO_COLOR environment variable
    import os
    if os.environ.get("NO_COLOR"):
        return False
    
    # Windows terminal support
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable ANSI escape sequences on Windows 10+
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    
    return True


# Predefined color functions for common log types
def success(text: str) -> str:
    """Green color for success messages."""
    return colorize(text, Colors.BRIGHT_GREEN, bold=True)


def error(text: str) -> str:
    """Red color for error messages."""
    return colorize(text, Colors.BRIGHT_RED, bold=True)


def warning(text: str) -> str:
    """Yellow color for warning messages."""
    return colorize(text, Colors.BRIGHT_YELLOW, bold=True)


def info(text: str) -> str:
    """Cyan color for info messages."""
    return colorize(text, Colors.BRIGHT_CYAN)


def debug(text: str) -> str:
    """Dim gray color for debug messages."""
    return colorize(text, Colors.BRIGHT_BLACK)


def highlight(text: str) -> str:
    """Magenta color for highlighted text."""
    return colorize(text, Colors.BRIGHT_MAGENTA, bold=True)


def key_value(key: str, value: str) -> str:
    """Format key-value pair with colors."""
    if not _supports_color():
        return f"{key}={value}"
    
    key_colored = colorize(key, Colors.CYAN)
    value_colored = colorize(value, Colors.BRIGHT_WHITE)
    return f"{key_colored}={value_colored}"


def emoji_log(emoji: str, message: str, level: str = "info") -> str:
    """
    Format log message with emoji and color based on level.
    
    Args:
        emoji: Emoji character
        message: Log message
        level: Log level (info, success, warning, error, debug)
        
    Returns:
        Formatted log message with emoji and color
    """
    level_colors = {
        "info": Colors.BRIGHT_CYAN,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "debug": Colors.BRIGHT_BLACK,
    }
    
    color = level_colors.get(level.lower(), Colors.WHITE)
    emoji_colored = colorize(emoji, color, bold=True)
    
    if not _supports_color():
        return f"{emoji} {message}"
    
    return f"{emoji_colored} {message}"


# HTTP Status code colors
def status_code(code: int) -> str:
    """Color HTTP status code based on range."""
    if not _supports_color():
        return str(code)
    
    if 200 <= code < 300:
        return colorize(str(code), Colors.BRIGHT_GREEN, bold=True)
    elif 300 <= code < 400:
        return colorize(str(code), Colors.BRIGHT_CYAN, bold=True)
    elif 400 <= code < 500:
        return colorize(str(code), Colors.BRIGHT_YELLOW, bold=True)
    elif 500 <= code:
        return colorize(str(code), Colors.BRIGHT_RED, bold=True)
    else:
        return str(code)


# Database operation colors
def db_operation(operation: str) -> str:
    """Color database operations."""
    if not _supports_color():
        return operation
    
    colors = {
        "SELECT": Colors.BRIGHT_BLUE,
        "INSERT": Colors.BRIGHT_GREEN,
        "UPDATE": Colors.BRIGHT_YELLOW,
        "DELETE": Colors.BRIGHT_RED,
        "COMMIT": Colors.BRIGHT_GREEN,
        "ROLLBACK": Colors.BRIGHT_RED,
        "BEGIN": Colors.BRIGHT_CYAN,
    }
    
    color = colors.get(operation.upper(), Colors.WHITE)
    return colorize(operation, color, bold=True)

