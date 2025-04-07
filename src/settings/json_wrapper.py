from __future__ import annotations

import json
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, LiteralString, Optional, TypeVar, cast

from pydantic import BaseModel, Field, ValidationError, field_validator

from model import config_keys

logger: logging.Logger = logging.getLogger(__name__)

SettingsType = config_keys.SecretKeys
T = TypeVar("T")

DEFAULT_CONFIG_PATH: Final[Path] = Path("configuration/settings.json")


class SettingsLoader(BaseModel):
    """Settings model with validation."""

    class Secret(BaseModel):
        token: str = Field(..., title="Bot Token", description="Discord bot token")

        @field_validator("token")
        @classmethod
        def validate_token(cls, v: str) -> str:
            if not v.strip():
                raise ValueError("Token cannot be empty or whitespace")
            return v

    secret: Secret


class Settings:
    """Settings manager with caching and validation."""

    _instance: Settings | None = None
    _data: SettingsLoader | None = None
    _config_path: Path = DEFAULT_CONFIG_PATH

    def __new__(cls) -> Settings:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, config_path: Path | None = None) -> None:
        """
        Initializes the JSON wrapper with an optional configuration file path.
        If a configuration path is provided, it sets the internal `_config_path`
        to the given path. Then, it loads the configuration data.

        Args:
            config_path (Path | None): Optional path to the configuration file.
                                       If not provided, the default path is used.
        Returns:
            None
        """

        if config_path:
            cls._config_path = config_path
        cls.load()

    @classmethod
    def load(cls) -> None:
        """
        Load the settings from the JSON configuration file.

        This method attempts to read and parse the JSON file specified by the `_config_path` attribute.
        It validates the settings and initializes the `_data` attribute with the parsed configuration.

        Raises:
            FileNotFoundError: If the configuration file does not exist at the specified path.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
            ValidationError: If the parsed settings do not meet the required validation criteria.
            Exception: For any other unexpected errors during the loading process.

        Logs:
            - Critical errors for missing files, invalid JSON, validation issues, or unexpected errors.
            - Informational message upon successful loading of settings.

        Exits:
            The application will terminate with a non-zero exit code if any critical error occurs.
        """

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
    def _validate_required_settings(cls) -> None:
        """
        Validates that all required settings are properly loaded and accessible.
        This method checks if the settings data has been loaded and ensures that
        all settings defined in the `SettingsType` enumeration can be accessed
        without errors. If the settings data is not loaded, a `RuntimeError` is raised.
        If any required setting is missing or inaccessible, a `ValueError` is raised
        with details about the missing setting.

        Raises:
            RuntimeError: If the settings data has not been loaded.
            ValueError: If a required setting is missing or cannot be accessed.
        """

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
        Retrieve a value from the settings data using a dot-separated key.

        Args:
            key (SettingsType): A dot-separated key representing the path to the desired value.
            default (Optional[T], optional): A default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value associated with the specified key, or the default value if the key is not found.

        Raises:
            ValueError: If the settings data has not been loaded.
            AttributeError: If the key is not found and no default value is provided.
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
        """
        Retrieves the configuration file path.

        Returns:
            Path: The path to the configuration file.
        """

        return cls._config_path
