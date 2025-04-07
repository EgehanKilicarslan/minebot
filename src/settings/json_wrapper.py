import json
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, LiteralString, Optional, TypeVar, cast

from pydantic import BaseModel, Field, ValidationError, field_validator

from model import config_keys

logger: logging.Logger = logging.getLogger(__name__)

SettingsType = config_keys.SecretEnum
T = TypeVar("T")

DEFAULT_CONFIG_PATH: Final[Path] = Path("configuration/settings.json")


class SettingsLoader(BaseModel):
    """Settings model with validation."""

    class Secret(BaseModel):
        token: str = Field(
            ...,
            title="Bot Token",
            description="Discord bot token",
            min_length=50,  # Discord tokens are typically longer
        )

        @field_validator("token")
        @classmethod
        def validate_token(cls, v: str) -> str:
            if not v.strip():
                raise ValueError("Token cannot be empty or whitespace")
            return v

    secret: Secret


class Settings:
    """Settings manager with caching and validation."""

    _instance: Optional["Settings"] = None
    _data: Optional[SettingsLoader] = None
    _config_path: Path = DEFAULT_CONFIG_PATH

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, config_path: Optional[Path] = None) -> None:
        """Initialize settings with optional custom config path."""
        if config_path:
            cls._config_path = config_path
        cls.load()

    @classmethod
    def load(cls) -> None:
        """Load settings from file with error handling."""
        try:
            if not cls._config_path.exists():
                raise FileNotFoundError(f"Settings file not found at {cls._config_path}")

            with cls._config_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
                cls._data = SettingsLoader(**data)
                cls._validate_required_settings()
                logger.info("Settings loaded successfully")

        except FileNotFoundError as e:
            logger.critical(f"Configuration error: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON in settings file: {e}")
            sys.exit(1)
        except ValidationError as e:
            logger.critical("Invalid settings configuration:")
            for error in e.errors():
                field_path: str = " -> ".join(str(loc) for loc in error["loc"])
                logger.critical(f"• {field_path}: {error['msg']}")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Unexpected error loading settings: {e}")
            sys.exit(1)

    @classmethod
    def reload(cls) -> None:
        """Reload settings from file."""
        cls._data = None  # Clear cache
        cls.load()

    @classmethod
    def _validate_required_settings(cls) -> None:
        """Validate that all required settings are present."""
        if cls._data is None:
            raise RuntimeError("Settings not loaded")

        # Validate all enum values can be accessed
        for setting in SettingsType:
            try:
                cls.get(setting)
            except AttributeError as e:
                logger.critical(f"Missing required setting: {setting.value}")
                raise ValueError(f"Missing required setting: {setting.value}") from e

    @classmethod
    @lru_cache(maxsize=128)
    def get(cls, key: SettingsType, default: Optional[T] = None) -> Any:
        """
        Get the value of a setting by its key with caching.

        Args:
            key: The settings enum key
            default: Optional default value if not found

        Returns:
            The setting value

        Raises:
            ValueError: If settings are not loaded
            AttributeError: If setting key doesn't exist
        """
        if cls._data is None:
            raise ValueError("Settings not loaded")

        try:
            parts: list[LiteralString] = key.value.split(".")
            value: Any = cls._data

            for part in parts:
                value = getattr(value, part)

            return cast(T, value)
        except AttributeError:
            if default is not None:
                return default
            raise

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the current config file path."""
        return cls._config_path
