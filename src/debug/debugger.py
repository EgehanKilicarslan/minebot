import json
import logging
import logging.config
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar, Dict, Final, Optional

from model.ready_keys import LogStyle


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored log output with improved readability."""

    # Cache format strings to avoid rebuilding them for each log record
    _FORMATS: ClassVar[Dict[str, str]] = {}

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color coding and improved structure.

        Args:
            record: The log record to format

        Returns:
            Formatted log string with color codes
        """
        # Get cached format for this level if available
        if record.levelname not in self._FORMATS:
            # Get styling
            level_color = LogStyle[record.levelname].value
            reset = LogStyle.RESET.value
            timestamp_color = LogStyle.TIMESTAMP.value
            name_color = LogStyle.NAME.value
            bracket = LogStyle.BRACKET.value
            arrow = LogStyle.ARROW.value

            # Create cached format string for this level
            self._FORMATS[record.levelname] = (
                f"{bracket}[{level_color}{record.levelname:4}{reset}{bracket}] "
                f"{bracket}[{name_color}%(name)-8s{bracket}] "
                f"{bracket}[{timestamp_color}%(asctime)s{bracket}] "
                f"{arrow}→ "
                f"{level_color}%(message)s{reset}"
            )

        # Set format for this record
        self._style._fmt = self._FORMATS[record.levelname]

        # Apply standard formatting
        return super().format(record)


# Configuration constants
DEFAULT_CONFIG_PATH: Final[Path] = Path("configuration/debug.json")
FALLBACK_CONFIG: Final[Dict[str, Any]] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": f"{ColoredFormatter.__module__}.{ColoredFormatter.__name__}",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "standard": {
            "format": "[%(levelname)4s] [%(name)-8s] [%(asctime)s] → %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored",
            "stream": "ext://sys.stdout",
        },
        # Add file handler for production environment
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "logs/minebot.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "minebot": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "hikari": {"level": "INFO", "handlers": ["console", "file"], "propagate": False},
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console", "file"],
    },
}


def setup_logging(config_path: Optional[Path] = None) -> bool:
    """
    Set up logging configuration from JSON file with fallback options.

    Args:
        config_path: Optional custom path to logging config file

    Returns:
        True if configuration was successful, False otherwise
    """
    try:
        config_path = config_path or DEFAULT_CONFIG_PATH

        # Ensure logs directory exists for file handlers
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        if config_path.exists():
            with config_path.open("rt", encoding="utf-8") as f:
                config: Dict[str, Any] = json.load(f)
        else:
            config = FALLBACK_CONFIG

        logging.config.dictConfig(config)
        return True

    except (json.JSONDecodeError, ValueError) as e:
        # Handle specific formatting errors in the config file
        _setup_emergency_logging()
        logging.error(f"Invalid logging configuration format: {e}. Using basic configuration.")
        return False
    except (PermissionError, OSError) as e:
        # Handle file access errors
        _setup_emergency_logging()
        logging.error(
            f"Could not access logging configuration file: {e}. Using basic configuration."
        )
        return False
    except Exception as e:
        # Catch all remaining exceptions
        _setup_emergency_logging()
        logging.error(f"Failed to configure logging: {e}. Using basic configuration.")
        return False


def _setup_emergency_logging() -> None:
    """Configure basic logging when the main configuration fails."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@lru_cache(maxsize=128)
def get_logger(name: str) -> logging.Logger:
    """
    Get a cached logger with the minebot namespace.

    Args:
        name: Logger name

    Returns:
        Logger instance with minebot namespace
    """
    return logging.getLogger(f"minebot.{name}")
