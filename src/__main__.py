import asyncio
import sys
from logging import Logger

import hikari
import lightbulb
from lightbulb import GatewayEnabledClient

import events
import extensions
from database import close_database, initialize_database
from debug import get_logger, setup_logging
from model import SecretKeys
from settings import Localization, Settings

if __name__ == "__main__":
    setup_logging()

    logger: Logger = get_logger(__name__)
    logger.info("Starting bot initialization")

    try:
        Settings.initialize()
        Localization.initialize()
        asyncio.run(initialize_database())

        bot = hikari.GatewayBot(
            token=Settings.get(SecretKeys.TOKEN),
            intents=hikari.Intents.ALL,
            suppress_optimization_warning=True,
            banner=None,
        )

        client: GatewayEnabledClient = lightbulb.client_from_app(
            bot, localization_provider=Localization.serialize()
        )

        @bot.listen(hikari.StartingEvent)
        async def on_starting(_: hikari.StartingEvent) -> None:
            logger.info("Starting bot")
            await client.load_extensions_from_package(events)
            await client.load_extensions_from_package(extensions, recursive=True)
            await client.start()

        @bot.listen(hikari.StoppingEvent)
        async def on_stopping(_: hikari.StoppingEvent) -> None:
            logger.info("Stopping bot")
            await client.stop()
            await close_database()

        bot.run()
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)
