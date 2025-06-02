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


class MessageType(Enum):
    """Message types for Minecraft server messages"""

    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARN = "WARN"
    ERROR = "ERROR"
    QUESTION = "QUESTION"
    ANNOUNCE = "ANNOUNCE"
    NO_PREFIX = "NO_PREFIX"


class PunishmentType(str, Enum):
    """Types of punishments that can be applied to users"""

    BAN = "ban"
    UNBAN = "unban"
    TIMEOUT = "timeout"
    UNTIMEOUT = "untimeout"


class PunishmentSource(str, Enum):
    """Sources of punishment for users"""

    DISCORD = "discord"
    MINECRAFT = "minecraft"
