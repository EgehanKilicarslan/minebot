from enum import Enum


class CommandKeys(Enum):
    """Command keys for the bot"""

    BAN_LABEL = "ban.command.label"
    BAN_DESCRIPTION = "ban.command.description"
    BAN_OPTIONS = "ban.command.options"


class MessageKeys(Enum):
    """Message keys for the bot"""

    BAN_COMMAND_USER_SUCCESS = "ban.messages.user.success"

    ERROR_TITLE = "error.title"
    ERROR_UNKNOWN = "error.unknown"
