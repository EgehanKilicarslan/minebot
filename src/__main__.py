import sys
from logging import Logger

import hikari
import lightbulb

from debug.debugger import get_logger, setup_logging
from model.config_keys import SecretEnum
from settings.json_wrapper import Settings

if __name__ == "__main__":
    setup_logging()

    logger: Logger = get_logger(__name__)
    logger.info("Starting bot initialization")

    try:
        Settings.initialize()

        bot = hikari.GatewayBot(
            token=Settings.get(SecretEnum.TOKEN),
            intents=hikari.Intents.ALL,
            suppress_optimization_warning=True,
            banner=None,
        )

        client = lightbulb.client_from_app(bot)

        @bot.listen(hikari.StartingEvent)
        async def on_starting(_: hikari.StartingEvent) -> None:
            logger.info("Starting bot")
            await client.start()

        @bot.listen(hikari.StoppingEvent)
        async def on_stopping(_: hikari.StoppingEvent) -> None:
            logger.info("Stopping bot")
            await client.stop()

        bot.run()
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)
