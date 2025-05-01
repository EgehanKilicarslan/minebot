import asyncio
from logging import Logger

import hikari

from data_types import TimedDict, TimedSet
from database.schemas import UserSchema
from database.services import UserService
from debug import get_logger
from websocket.schemas.response import PlayerServerCheckSchema, PlayerStatusCheckSchema

logger: Logger = get_logger(__name__)


MINECRAFT_SERVERS: list[str] = []
ONLINE_PLAYERS: TimedSet[str] = TimedSet[str](10)
PLAYER_SERVERS: TimedDict[str, str] = TimedDict[str, str](10)


class MinecraftHelper:
    @staticmethod
    async def _resolve_identifier(
        user: hikari.User | None = None,
        username: str | None = None,
        uuid: str | None = None,
    ) -> tuple[str, bool]:
        """
        Resolves a player identifier (username or UUID) from the provided parameters.

        Args:
            user: Discord user to check (their UUID will be retrieved from database)
            username: Minecraft username
            uuid: Minecraft UUID

        Returns:
            Tuple containing (identifier, is_from_database)

        Raises:
            ValueError: If invalid parameter combination is provided
        """
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
                logger.debug(f"No Minecraft UUID found for Discord user {user.id}")
                return "", False

            uuid = schema.minecraftUUID
            logger.debug(f"Found Minecraft UUID {uuid} for Discord user {user.id}")
            return uuid, True

        # Validate we have exactly one identifier
        elif not bool(username) ^ bool(uuid):  # XOR operation
            logger.error(f"Invalid parameter combination: username={username}, uuid={uuid}")
            raise ValueError("Exactly one of 'username' or 'uuid' must be provided")

        # Return the identifier
        identifier: str = username or uuid or ""
        return identifier, False

    @staticmethod
    async def fetch_player_status(
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
        if not MINECRAFT_SERVERS:
            logger.warning("No Minecraft servers available, cannot check player status")
            return False

        logger.debug(
            f"Checking player status with: user={user and user.id}, username={username}, uuid={uuid}"
        )

        identifier, from_db = await MinecraftHelper._resolve_identifier(user, username, uuid)
        if not identifier:
            return False

        logger.debug(f"Using identifier: {identifier}")

        # Quick check if already in cache before making request
        if ONLINE_PLAYERS.contains(identifier):
            logger.debug(f"Player {identifier} found in cache, returning online status")
            return True

        # Request status check from websocket
        logger.debug(f"Player {identifier} not in cache, requesting status from WebSocket")
        from websocket import WebSocketManager

        await WebSocketManager.send_message(
            PlayerStatusCheckSchema(
                username=None if from_db else username, uuid=identifier if from_db else uuid
            )
        )

        logger.debug(f"Waiting {response_timeout}s for WebSocket response")
        await asyncio.sleep(response_timeout)

        is_online = ONLINE_PLAYERS.contains(identifier)
        logger.debug(f"Player {identifier} is {'online' if is_online else 'offline'}")
        return is_online

    @staticmethod
    async def fetch_player_server(
        user: hikari.User | None = None,
        username: str | None = None,
        uuid: str | None = None,
        response_timeout: float = 1.0,
    ) -> str | None:
        """
        Check which server a Minecraft player is currently on.

        Args:
            user: Discord user to check (their UUID will be retrieved from database)
            username: Minecraft username (mutually exclusive with user and uuid)
            uuid: Minecraft UUID (mutually exclusive with user and username)
            response_timeout: Timeout for the response from the websocket

        Returns:
            Server name if player is online, None otherwise

        Raises:
            ValueError: If invalid parameter combination is provided

        Note:
            When calling from a Discord interaction, consider using ctx.defer() before
            calling this method as it may take longer than Discord's 3-second timeout.
        """
        if not MINECRAFT_SERVERS:
            logger.warning("No Minecraft servers available, cannot check player status")
            return None

        logger.debug(
            f"Checking player server with: user={user and user.id}, username={username}, uuid={uuid}"
        )

        identifier, from_db = await MinecraftHelper._resolve_identifier(user, username, uuid)
        if not identifier:
            return None

        logger.debug(f"Using identifier: {identifier}")

        # Quick check if already in cache before making request
        if identifier in PLAYER_SERVERS:
            logger.debug(
                f"Player {identifier} found in cache, returning server: {PLAYER_SERVERS[identifier]}"
            )
            return PLAYER_SERVERS[identifier]

        # Check online status first, this already includes waiting for the response
        is_online = await MinecraftHelper.fetch_player_status(
            uuid=identifier if from_db else uuid,
            username=None if from_db else username,
            response_timeout=response_timeout,
        )

        if not is_online:
            logger.debug(f"Player {identifier} is offline, cannot fetch server")
            return None

        # After status check, see if server info was populated
        if identifier in PLAYER_SERVERS:
            logger.debug(f"Server found in cache after status check: {PLAYER_SERVERS[identifier]}")
            return PLAYER_SERVERS[identifier]

        # If only one server is available, we know the player must be there
        if len(MINECRAFT_SERVERS) == 1:
            logger.debug(f"Only one server available: {MINECRAFT_SERVERS[0]}")
            return MINECRAFT_SERVERS[0]

        # If we need to explicitly request server info
        logger.debug(f"Player {identifier} is online but server unknown, requesting from WebSocket")
        from websocket import WebSocketManager

        await WebSocketManager.send_message(
            PlayerServerCheckSchema(
                username=None if from_db else username, uuid=identifier if from_db else uuid
            )
        )

        logger.debug(f"Waiting {response_timeout}s for WebSocket response")
        await asyncio.sleep(response_timeout)

        server = PLAYER_SERVERS.get(identifier)
        logger.debug(f"Player {identifier} is on server: {server}")
        return server
