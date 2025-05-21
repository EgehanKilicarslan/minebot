from logging import Logger
from typing import Sequence

import hikari
import lightbulb
import toolbox

from debug import get_logger
from helper import WikiHelper
from model import SecretKeys
from settings import Localization, Settings

REQUIRED_PERMISSIONS = 1829587348619263  # Administrator permissions value
BOOSTER_ROLE: hikari.Role | None = None

loader = lightbulb.Loader()
logger: Logger = get_logger(__name__)


@loader.listener(hikari.ShardReadyEvent)
async def on_ready(event: hikari.ShardReadyEvent) -> None:
    global BOOSTER_ROLE

    try:
        # Fetch and validate default guild
        guild: hikari.Guild = await event.app.rest.fetch_guild(
            Settings.get(SecretKeys.DEFAULT_GUILD)
        )
        if guild is None:
            logger.critical("Failed to retrieve the guild.")
            raise Exception("Failed to retrieve the guild.")
        logger.info(f"Bot connected to guild: {guild.name} (ID: {guild.id})")

        # Set guild language
        preferred_locale = hikari.Locale(guild.preferred_locale)
        Localization.set_guild_language(preferred_locale)
        WikiHelper.set_guild_language(preferred_locale)
        logger.info(f"Guild language set to: {preferred_locale}")

        # Verify bot member
        my_member: hikari.Member | None = guild.get_my_member()
        if my_member is None:
            logger.critical("Failed to retrieve bot member.")
            raise Exception("Failed to retrieve bot member.")

        # Check permissions
        if toolbox.calculate_permissions(my_member).value != REQUIRED_PERMISSIONS:
            logger.critical("Bot does not have administrator permissions.")
            raise Exception("Bot does not have administrator permissions.")
        logger.info("Bot has the required administrator permissions.")

        guild_roles: Sequence[hikari.Role] = await guild.fetch_roles()
        BOOSTER_ROLE = next((r for r in guild_roles if r.is_premium_subscriber_role), None)

        logger.info("Bot is ready and fully operational.")
    except Exception as e:
        logger.critical(f"An error occurred during the ready event: {e}", exc_info=True)
        raise
