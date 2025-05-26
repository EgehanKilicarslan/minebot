import hikari
import toolbox

from core import GlobalState
from helper.message import MessageHelper
from model.message import MessageKeys


class PunishmentHelper:
    _bot_member: hikari.Member | None = None

    @classmethod
    def _get_bot_member(cls) -> hikari.Member:
        """Get and cache the bot member if not already cached."""
        if cls._bot_member is None:
            cls._bot_member = GlobalState.bot.get_member()
        return cls._bot_member

    @classmethod
    def can_moderate(
        cls,
        target: hikari.Member,
        moderator: hikari.Member,
        permission: hikari.Permissions = hikari.Permissions.NONE,
    ) -> bool:
        """Check if both moderator and bot can moderate the target.

        Args:
            target: Member to moderate
            moderator: Member attempting moderation
            permission: Required permission for moderation

        Returns:
            bool: True if moderation is allowed
        """
        try:
            bot_member = cls._get_bot_member()
        except ValueError:
            return False

        return toolbox.can_moderate(moderator, target, permission) and toolbox.can_moderate(
            bot_member, target, permission
        )

    @staticmethod
    def get_reason(reason: str | None, locale: str | hikari.Locale) -> tuple[str, str]:
        """Get reason for a punishment action with localization support.

        Args:
            reason: The reason for the punishment, if any
            locale: The locale for localization if no reason is provided

        Returns:
            A tuple of (reason_text, reason_text) or (localized_no_reason, localized_no_reason)
        """
        if reason:
            return reason, reason

        messages = MessageHelper(
            MessageKeys.GENERAL_NO_REASON, user_locale=locale
        ).get_localized_message_pair("text")

        return (str(messages[0]), str(messages[1]))
