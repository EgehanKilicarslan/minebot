import asyncio
import os
import sys
from logging import Logger

import hikari
import lightbulb
from lightbulb import GatewayEnabledClient

import events
import extensions
from database import close_database, initialize_database
from debug import get_logger, setup_logging
from exceptions.command import CommandExecutionError
from exceptions.utility import EmptyException
from hooks.database import add_or_update_user
from model import BotKeys, SecretKeys
from settings import Localization, Settings
from websocket import WebSocketServer

if __name__ == "__main__":
    setup_logging()

    logger: Logger = get_logger(__name__)
    logger.info("Starting bot initialization")

    if os.name != "nt":
        import uvloop

        logger.debug("Using uvloop as the event loop policy")
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    else:
        logger.debug("Using default asyncio event loop policy")

    try:
        Settings.initialize()
        Localization.initialize()
        websocket = WebSocketServer()

        bot = hikari.GatewayBot(
            token=Settings.get(SecretKeys.TOKEN),
            intents=hikari.Intents.ALL,
            suppress_optimization_warning=True,
            banner=None,
        )

        client: GatewayEnabledClient = lightbulb.client_from_app(
            bot, localization_provider=Localization.serialize(), hooks=[add_or_update_user]
        )

        @client.error_handler
        async def handler(exc: lightbulb.exceptions.ExecutionPipelineFailedException) -> bool:
            if not isinstance(exc, EmptyException):
                return True
            elif not isinstance(exc, CommandExecutionError):
                await exc.context.respond(content=exc.causes[0], ephemeral=True)
                return True
            return False

        @bot.listen(hikari.StartingEvent)
        async def on_starting(_: hikari.StartingEvent) -> None:
            logger.info("Starting bot")
            await initialize_database()
            await client.load_extensions_from_package(events)
            await client.load_extensions_from_package(extensions, recursive=True)
            await client.start()
            await websocket.start()

        @bot.listen(hikari.StoppingEvent)
        async def on_stopping(_: hikari.StoppingEvent) -> None:
            logger.info("Stopping bot")
            await websocket.stop()
            await client.stop()
            await close_database()

        bot.run(
            status=getattr(hikari.Status, Settings.get(BotKeys.STATUS)),
            activity=hikari.Activity(
                name=Settings.get(BotKeys.NAME),
                state=Settings.get(BotKeys.STATE),
                url=Settings.get(BotKeys.URL),
                type=getattr(hikari.ActivityType, Settings.get(BotKeys.TYPE)),
            ),
        )
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)
