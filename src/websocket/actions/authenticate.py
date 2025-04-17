from logging import Logger

from websockets import ServerConnection

from debug import get_logger
from websocket import websocket_action
from websocket.schemas import AuthenticateSchema

logger: Logger = get_logger(__name__)


@websocket_action("authenticate", AuthenticateSchema)
async def authenticate(websocket: ServerConnection, data: AuthenticateSchema) -> None:
    pass
