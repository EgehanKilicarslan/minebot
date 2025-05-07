from enum import Enum


class CommandKeys(Enum):
    """Command keys for the bot"""

    BAN_LABEL = "ban.command.label"
    BAN_DESCRIPTION = "ban.command.description"
    BAN_OPTIONS = "ban.command.options"


class MessageKeys(Enum):
    """Message keys for the bot"""

    BAN_COMMAND_USER_SUCCESS = "ban.messages.user.success"

    UNKNOWN_ERROR = "error.unknown_error"
    COMMAND_EXECUTION_ERROR = "error.command_execution_error"
    USER_RECORD_NOT_FOUND = "error.user_record_not_found"
    ACCOUNT_ALREADY_LINKED = "error.account_already_linked"
    ACCOUNT_NOT_LINKED = "error.account_not_linked"
    PLAYER_NOT_ONLINE = "error.player_not_online"
