from enum import Enum


class CommandKeys(Enum):
    """Command keys for the bot"""

    LINK_ACCOUNT_LABEL = "commands.link_account.command.label"
    LINK_ACCOUNT_DESCRIPTION = "commands.link_account.command.description"
    LINK_ACCOUNT_OPTIONS = "commands.link_account.command.options"

    WITHDRAW_REWARDS_LABEL = "commands.withdraw_rewards.command.label"
    WITHDRAW_REWARDS_DESCRIPTION = "commands.withdraw_rewards.command.description"

    BAN_LABEL = "commands.ban.command.label"
    BAN_DESCRIPTION = "commands.ban.command.description"
    BAN_OPTIONS = "commands.ban.command.options"

    UNBAN_LABEL = "commands.unban.command.label"
    UNBAN_DESCRIPTION = "commands.unban.command.description"
    UNBAN_OPTIONS = "commands.unban.command.options"

    TIMEOUT_LABEL = "commands.timeout.command.label"
    TIMEOUT_DESCRIPTION = "commands.timeout.command.description"
    TIMEOUT_OPTIONS = "commands.timeout.command.options"

    UNTIMEOUT_LABEL = "commands.untimeout.command.label"
    UNTIMEOUT_DESCRIPTION = "commands.untimeout.command.description"
    UNTIMEOUT_OPTIONS = "commands.untimeout.command.options"

    SUGGEST_LABEL = "commands.suggest.command.label"
    SUGGEST_DESCRIPTION = "commands.suggest.command.description"

    WIKI_LABEL = "commands.wiki.command.label"
    WIKI_DESCRIPTION = "commands.wiki.command.description"
    WIKI_OPTIONS = "commands.wiki.command.options"


class MessageKeys(Enum):
    """Message keys for the bot"""

    GUILD_BOOST_LOG_SUCCESS = "events.guild_boost.messages.log.success"

    LINK_ACCOUNT_MINECRAFT_CONFIRMATION_CODE = (
        "commands.link_account.messages.minecraft.confirmation_code"
    )
    LINK_ACCOUNT_MINECRAFT_SUCCESS = "commands.link_account.messages.minecraft.success"
    LINK_ACCOUNT_MINECRAFT_FAILURE = "commands.link_account.messages.minecraft.failure"
    LINK_ACCOUNT_USER_SUCCESS = "commands.link_account.messages.user.success"
    LINK_ACCOUNT_USER_FAILURE = "commands.link_account.messages.user.failure"
    LINK_ACCOUNT_LOG_SUCCESS = "commands.link_account.messages.log.success"
    LINK_ACCOUNT_LOG_FAILURE = "commands.link_account.messages.log.failure"

    WITHDRAW_REWARDS_USER_SUCCESS = "commands.withdraw_rewards.messages.user.success"
    WITHDRAW_REWARDS_USER_FAILURE = "commands.withdraw_rewards.messages.user.failure"
    WITHDRAW_REWARDS_LOG_SUCCESS = "commands.withdraw_rewards.messages.log.success"
    WITHDRAW_REWARDS_LOG_FAILURE = "commands.withdraw_rewards.messages.log.failure"

    BAN_COMMAND_USER_SUCCESS = "commands.ban.messages.user.success"
    BAN_COMMAND_LOG_SUCCESS = "commands.ban.messages.log.success"

    UNBAN_COMMAND_USER_SUCCESS = "commands.unban.messages.user.success"
    UNBAN_COMMAND_LOG_SUCCESS = "commands.unban.messages.log.success"

    TIMEOUT_COMMAND_USER_SUCCESS = "commands.timeout.messages.user.success"
    TIMEOUT_COMMAND_LOG_SUCCESS = "commands.timeout.messages.log.success"

    UNTIMEOUT_COMMAND_USER_SUCCESS = "commands.untimeout.messages.user.success"
    UNTIMEOUT_COMMAND_LOG_SUCCESS = "commands.untimeout.messages.log.success"

    CLEAR_COMMAND_USER_SUCCESS = "commands.clear.messages.user.success"
    CLEAR_COMMAND_LOG_SUCCESS = "commands.clear.messages.log.success"

    LOCK_COMMAND_USER_SUCCESS = "commands.lock.messages.user.success"
    LOCK_COMMAND_LOG_SUCCESS = "commands.lock.messages.log.success"

    UNLOCK_COMMAND_USER_SUCCESS = "commands.unlock.messages.user.success"
    UNLOCK_COMMAND_LOG_SUCCESS = "commands.unlock.messages.log.success"

    SUGGEST_MINECRAFT_APPROVE = "commands.suggest.messages.minecraft.approve"
    SUGGEST_MINECRAFT_REJECT = "commands.suggest.messages.minecraft.reject"
    SUGGEST_USER_SUCCESS = "commands.suggest.messages.user.success"
    SUGGEST_USER_FAILURE = "commands.suggest.messages.user.failure"
    SUGGEST_PENDING_SUCCESS = "commands.suggest.messages.pending.success"
    SUGGEST_PENDING_FAILURE = "commands.suggest.messages.pending.failure"
    SUGGEST_RESULT_APPROVE = "commands.suggest.messages.result.approve"
    SUGGEST_RESULT_REJECT = "commands.suggest.messages.result.reject"

    WIKI_COMMAND_USER_SUCCESS = "commands.wiki.messages.user.success"
    WIKI_COMMAND_USER_FAILURE = "commands.wiki.messages.user.failure"

    GENERAL_SUCCESS = "general.success"
    GENERAL_FAILURE = "general.failure"
    GENERAL_NO_REASON = "general.no_reason"

    UNKNOWN_ERROR = "error.unknown_error"
    TIMEOUT_ERROR = "error.timeout_error"
    USER_NOT_FOUND = "error.user_not_found"
    MEMBER_NOT_FOUND = "error.member_not_found"
    CHANNEL_NOT_FOUND = "error.channel_not_found"
    COMMAND_EXECUTION_ERROR = "error.command_execution_error"
    USER_RECORD_NOT_FOUND = "error.user_record_not_found"
    ACCOUNT_ALREADY_LINKED = "error.account_already_linked"
    ACCOUNT_NOT_LINKED = "error.account_not_linked"
    PLAYER_NOT_ONLINE = "error.player_not_online"
    CAN_NOT_MODERATE = "error.can_not_moderate"
    USER_ALREADY_TIMED_OUT = "error.user_already_timed_out"
    USER_NOT_TIMED_OUT = "error.user_not_timed_out"


class ModalKeys(Enum):
    """Modal keys for the bot"""

    LINK_ACCOUNT_CONFIRMATION = "commands.link_account.modal.confirmation"
    SUGGEST_SEND = "commands.suggest.modal.send"
    SUGGEST_RESPOND = "commands.suggest.modal.respond"


class MenuKeys(Enum):
    """Menu keys for the bot"""

    SUGGEST_CONFIRMATION = "commands.suggest.menu.confirmation"


class TimeUnitKeys(Enum):
    """Time unit keys for the bot"""

    YEAR = "time_units.year"
    MONTH = "time_units.month"
    WEEK = "time_units.week"
    DAY = "time_units.day"
    HOUR = "time_units.hour"
    MINUTE = "time_units.minute"
    SECOND = "time_units.second"
