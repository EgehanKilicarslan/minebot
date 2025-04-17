import json
from logging import Logger

from websockets import ServerConnection

from debug import get_logger
from model import WebSocketKeys
from settings import Settings
from websocket import authenticated_client, websocket_action
from websocket.schemas import AuthenticateSchema

logger: Logger = get_logger(__name__)


@websocket_action("authenticate", AuthenticateSchema)
async def authenticate(websocket: ServerConnection, data: AuthenticateSchema) -> None:
    client_id = id(websocket)
    auth_password: str = Settings.get(WebSocketKeys.PASSWORD)

    if data.password != auth_password:
        logger.warning(f"Authentication failed for client [id={client_id}]: Invalid credentials")
        await websocket.close(1008, "Authentication failed: Invalid credentials provided")
        return

    authenticated_client[client_id] = (websocket, data)

    logger.info(f"Client authenticated successfully [id={client_id}]")
    await websocket.send(json.dumps({"status": "success", "message": "Authentication successful"}))
