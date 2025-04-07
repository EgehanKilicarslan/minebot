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

        logger.info("Starting bot")
        bot.run()
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)
