from logging import Logger

import hikari

from debug.debugger import get_logger, setup_logging
from model.settings_enums import SecretEnum
from settings.json_wrapper import Settings

if __name__ == "__main__":
    setup_logging()

    logger: Logger = get_logger(__name__)
    logger.info("Starting bot initialization")

    Settings.initialize()
    bot = hikari.GatewayBot(token=Settings.get(SecretEnum.TOKEN))
    bot.run()
