from logging import Logger

from websockets import ServerConnection

from debug import get_logger
from helper import PLAYER_SERVERS

from ...action_registry import websocket_action
from ...schemas.response import PlayerServerCheckSchema

logger: Logger = get_logger(__name__)


@websocket_action("player-server-check", PlayerServerCheckSchema)
async def player_server_check(websocket: ServerConnection, data: PlayerServerCheckSchema) -> None:
    logger.debug(
        f"Received player status check request: username={data.username}, uuid={data.uuid}, server={data.server}"
    )

    # Validate the provided username or UUID
    if data.server:
        if data.username:
            PLAYER_SERVERS[data.username] = data.server  # Assign server to username
        if data.uuid:
            PLAYER_SERVERS[data.uuid] = data.server  # Assign server to UUID
