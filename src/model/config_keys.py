from enum import Enum


class SecretKeys(Enum):
    """Enum for secret keys in the configuration."""

    TOKEN = "secret.token"
    DEFAULT_GUILD = "secret.default_guild"


class DatabaseKeys(Enum):
    URL = "database.url"


class WebSocketKeys(Enum):
    HOST = "server.websocket.host"
    PORT = "server.websocket.port"
    ALLOWED_IP = "server.websocket.auth.allowed_ip"
    PASSWORD = "server.websocket.auth.password"


class CommandsKeys(Enum):
    BAN = "commands.ban"
