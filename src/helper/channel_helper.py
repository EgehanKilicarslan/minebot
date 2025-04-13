from logging import Logger
from typing import TypeVar

import hikari
import lightbulb

from debug import get_logger

logger: Logger = get_logger(__name__)

T = TypeVar("T", bound=hikari.PartialChannel)


class ChannelHelper:
    @staticmethod
    async def fetch_channel(
        client: lightbulb.Client,
        channel_id: int,
        channel_type: type[T] = hikari.PartialChannel,
    ) -> T:
        """
        Fetches a Discord channel by ID and verifies its type.

        This async function attempts to retrieve a channel from Discord using the provided ID,
        then checks if the retrieved channel matches the expected channel type.

        Args:
            client (lightbulb.Client): The Discord client to use for API requests
            channel_id (int): The ID of the channel to fetch
            channel_type (type[hikari.PartialChannel]): The expected channel type. Defaults to hikari.PartialChannel

        Returns:
            type[hikari.PartialChannel]: The fetched channel, cast to the specified type

        Raises:
            ValueError: If the channel doesn't exist or isn't of the expected type
            Exception: If an unexpected error occurs during the fetch operation
        """
        try:
            channel: hikari.PartialChannel = await client.rest.fetch_channel(channel_id)

            if isinstance(channel, channel_type):
                logger.debug(f"Fetched channel {channel_id} of type {channel_type.__name__}")
                return channel  # Type is automatically cast to T
            else:
                logger.warning(
                    f"Channel {channel_id} exists but is of type {type(channel).__name__}, expected {channel_type.__name__}"
                )
                raise ValueError(
                    f"Channel {channel_id} is not of expected type {channel_type.__name__}"
                )

        except hikari.NotFoundError:
            logger.warning(f"Channel with ID {channel_id} not found")
            raise ValueError(f"Channel with ID {channel_id} not found")
        except Exception as e:
            logger.error(f"Unexpected error fetching channel {channel_id}: {e}")
            raise e
