from enum import Enum


class SecretKeys(Enum):
    """Enum for secret keys in the configuration."""

    TOKEN = "secret.token"
    DEFAULT_GUILD = "secret.default_guild"


class DatabaseKeys(Enum):
    URL = "database.url"


class WebSocketKeys(Enum):
    HOST = "websocket.server.host"
    PORT = "websocket.server.port"


class CommandsKeys(Enum):
    BAN = "commands.ban"
