import hikari

from core import GlobalState
from model import SecretKeys
from settings import Settings


class UserHelper:
    @staticmethod
    async def fetch_member(user: hikari.User) -> hikari.Member | None:
        """Fetch a member from the default guild."""
        try:
            return await GlobalState.bot.get_bot().rest.fetch_member(
                Settings.get(SecretKeys.DEFAULT_GUILD), user
            )
        except (hikari.NotFoundError, Exception):
            return None
