from logging import Logger

from websockets import ServerConnection

from debug import get_logger
from helper import ONLINE_PLAYERS
from helper.minecraft import PLAYER_UUIDS

from ...action_registry import websocket_action
from ...schemas.response import PlayerStatusCheckSchema

logger: Logger = get_logger(__name__)


@websocket_action("player-status-check", PlayerStatusCheckSchema)
async def player_status_check(websocket: ServerConnection, data: PlayerStatusCheckSchema) -> None:
    logger.debug(
        f"Received player status check request: username={data.username}, uuid={data.uuid}, online={data.online}"
    )

    # Validate the provided username or UUID
    if data.online and data.username and data.uuid:
        ONLINE_PLAYERS.add(data.username)  # Assign username to online players
        ONLINE_PLAYERS.add(data.uuid)  # Assign UUID to online players
        PLAYER_UUIDS[data.username] = data.uuid  # Map username to UUID
