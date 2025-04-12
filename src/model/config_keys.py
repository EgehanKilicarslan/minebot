from enum import Enum


class SecretKeys(Enum):
    """Enum for secret keys in the configuration."""

    TOKEN = "secret.token"
    DEFAULT_GUILD = "secret.default_guild"


class DatabaseKeys(Enum):
    URL = "database.url"
