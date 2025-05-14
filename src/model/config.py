from enum import Enum


class SecretKeys(Enum):
    """Enum for secret keys in the configuration."""

    TOKEN = "secret.token"
    DEFAULT_GUILD = "secret.default_guild"


class DatabaseKeys(Enum):
    """Enum for database keys in the configuration."""

    URL = "database.url"


class BotKeys(Enum):
    """Enum for bot keys in the configuration."""

    STATUS = "bot.status"
    NAME = "bot.activity.name"
    STATE = "bot.activity.state"
    URL = "bot.activity.url"
    TYPE = "bot.activity.type"


class WebSocketKeys(Enum):
    """Enum for WebSocket keys in the configuration."""

    HOST = "server.websocket.host"
    PORT = "server.websocket.port"
    ALLOWED_IP = "server.websocket.auth.allowed_ip"
    PASSWORD = "server.websocket.auth.password"


class CommandsKeys(Enum):
    """Enum for command keys in the configuration."""

    LINK_ACCOUNT = "commands.link_account"
    WITHDRAW_REWARDS = "commands.withdraw_rewards"
    BAN = "commands.ban"
    WIKI = "commands.wiki"
