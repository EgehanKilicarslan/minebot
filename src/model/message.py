from enum import Enum


class CommandKeys(Enum):
    """Command keys for the bot"""

    LINK_ACCOUNT_LABEL = "link_account.command.label"
    LINK_ACCOUNT_DESCRIPTION = "link_account.command.description"
    LINK_ACCOUNT_OPTIONS = "link_account.command.options"

    WITHDRAW_REWARDS_LABEL = "withdraw_rewards.command.label"
    WITHDRAW_REWARDS_DESCRIPTION = "withdraw_rewards.command.description"

    BAN_LABEL = "ban.command.label"
    BAN_DESCRIPTION = "ban.command.description"
    BAN_OPTIONS = "ban.command.options"

    WIKI_LABEL = "wiki.command.label"
    WIKI_DESCRIPTION = "wiki.command.description"
    WIKI_OPTIONS = "wiki.command.options"


class MessageKeys(Enum):
    """Message keys for the bot"""

    LINK_ACCOUNT_MINECRAFT_CONFIRMATION_CODE = "link_account.messages.minecraft.confirmation_code"
    LINK_ACCOUNT_MINECRAFT_SUCCESS = "link_account.messages.minecraft.success"
    LINK_ACCOUNT_MINECRAFT_FAILURE = "link_account.messages.minecraft.failure"
    LINK_ACCOUNT_USER_SUCCESS = "link_account.messages.user.success"
    LINK_ACCOUNT_USER_FAILURE = "link_account.messages.user.failure"
    LINK_ACCOUNT_LOG_SUCCESS = "link_account.messages.log.success"
    LINK_ACCOUNT_LOG_FAILURE = "link_account.messages.log.failure"

    WITHDRAW_REWARDS_USER_SUCCESS = "withdraw_rewards.messages.user.success"
    WITHDRAW_REWARDS_USER_FAILURE = "withdraw_rewards.messages.user.failure"
    WITHDRAW_REWARDS_LOG_SUCCESS = "withdraw_rewards.messages.log.success"
    WITHDRAW_REWARDS_LOG_FAILURE = "withdraw_rewards.messages.log.failure"

    BAN_COMMAND_USER_SUCCESS = "ban.messages.user.success"

    WIKI_COMMAND_USER_SUCCESS = "wiki.messages.user.success"
    WIKI_COMMAND_USER_FAILURE = "wiki.messages.user.failure"

    UNKNOWN_ERROR = "error.unknown_error"
    TIMEOUT_ERROR = "error.timeout_error"
    COMMAND_EXECUTION_ERROR = "error.command_execution_error"
    USER_RECORD_NOT_FOUND = "error.user_record_not_found"
    ACCOUNT_ALREADY_LINKED = "error.account_already_linked"
    ACCOUNT_NOT_LINKED = "error.account_not_linked"
    PLAYER_NOT_ONLINE = "error.player_not_online"


class ModalKeys(Enum):
    """Modal keys for the bot"""

    LINK_ACCOUNT_CONFIRMATION = "link_account.modal.confirmation"


class ViewKeys(Enum):
    """View keys for the bot"""

    pass
