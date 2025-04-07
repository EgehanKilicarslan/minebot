from enum import Enum


class LogStyle(Enum):
    """Log styles with ANSI color and style codes"""

    DEBUG = "\033[36;1m"  # Bright Cyan
    INFO = "\033[32;1m"  # Bright Green
    WARNING = "\033[33;1m"  # Bright Yellow
    ERROR = "\033[31;1m"  # Bright Red
    CRITICAL = "\033[97;41m"  # White on Red
    TIMESTAMP = "\033[90m"  # Gray
    NAME = "\033[94;1m"  # Bright Blue
    RESET = "\033[0m"  # Reset
    ARROW = "\033[35;1m"  # Bright Magenta
    BRACKET = "\033[37;1m"  # Bright White
