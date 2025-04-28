import asyncio
from logging import Logger

import hikari

from data_types import TimedSet
from database.schemas import UserSchema
from database.services import UserService
from debug import get_logger
from websocket import WebSocketManager
from websocket.schemas import PlayerStatusCheckSchema

logger: Logger = get_logger(__name__)


ONLINE_PLAYERS: TimedSet = TimedSet[str](10)


class MinecraftHelper:
    @staticmethod
    async def check_player_status(
        user: hikari.User | None = None,
        username: str | None = None,
        uuid: str | None = None,
        response_timeout: float = 1.0,
    ) -> bool:
        """
        Check if a Minecraft player is online.

        Args:
            user: Discord user to check (their UUID will be retrieved from database)
            username: Minecraft username (mutually exclusive with user and uuid)
            uuid: Minecraft UUID (mutually exclusive with user and username)
            response_timeout: Timeout for the response from the websocket

        Returns:
            Whether the player is online

        Raises:
            ValueError: If invalid parameter combination is provided

        Note:
            When calling from a Discord interaction, consider using ctx.defer() before
            calling this method as it may take longer than Discord's 3-second timeout.
        """
        logger.debug(
            f"Checking player status with: user={user and user.id}, username={username}, uuid={uuid}"
        )

        # If user is provided, get their UUID from database
        if user:
            if username or uuid:
                logger.error(
                    f"Invalid parameter combination: user={user.id}, username={username}, uuid={uuid}"
                )
                raise ValueError("When 'user' is provided, 'username' and 'uuid' must be None")

            logger.debug(f"Looking up Minecraft UUID for Discord user {user.id}")
            schema: UserSchema | None = await UserService.get_user(user.id)
            if not schema or not schema.minecraftUUID:
                logger.error(f"No Minecraft UUID found for Discord user {user.id}")
                return False

            uuid = schema.minecraftUUID
            logger.debug(f"Found Minecraft UUID {uuid} for Discord user {user.id}")

        # Validate we have exactly one identifier
        elif not bool(username) ^ bool(uuid):  # XOR operation
            logger.error(f"Invalid parameter combination: username={username}, uuid={uuid}")
            raise ValueError("Exactly one of 'username' or 'uuid' must be provided")

        # Get the identifier to check
        identifier: str | None = username or uuid
        logger.debug(f"Using identifier: {identifier}")

        # Quick check if already in cache before making request
        if ONLINE_PLAYERS.contains(identifier):
            logger.debug(f"Player {identifier} found in cache, returning online status")
            return True

        # Request status check from websocket
        logger.debug(f"Player {identifier} not in cache, requesting status from WebSocket")
        await WebSocketManager.send_message(PlayerStatusCheckSchema(username=username, uuid=uuid))

        logger.debug(f"Waiting {response_timeout}s for WebSocket response")
        await asyncio.sleep(response_timeout)

        is_online = ONLINE_PLAYERS.contains(identifier)
        logger.debug(f"Player {identifier} is {'online' if is_online else 'offline'}")
        return is_online
