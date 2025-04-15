from logging import Logger

from websockets import ServerConnection

from debug import get_logger
from websocket import websocket_action
from websocket.schemas import AuthenticateSchema

logger: Logger = get_logger(__name__)


@websocket_action("authenticate", AuthenticateSchema)
async def authenticate(websocket: ServerConnection, data: AuthenticateSchema) -> None:
    user_registry: dict[str, int] = {}

    test_user: dict[str, str] = {"username": "test", "password": "test"}

    if data.username == test_user["username"] and data.password == test_user["password"]:
        # Store the username as key and websocket client id as value
        user_registry[data.username] = id(websocket)
        await websocket.send('{"action": "authenticate_response", "status": "ok"}')
        logger.debug(user_registry)
