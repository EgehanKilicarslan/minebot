from logging import Logger

from websockets import ServerConnection

from debug import get_logger
from websocket import websocket_action
from websocket.schemas import TestSchema

logger: Logger = get_logger(__name__)


@websocket_action("test", TestSchema)
async def test(websocket: ServerConnection, data: TestSchema) -> None:
    """
    Test action handler for WebSocket connections.

    Args:
        websocket: The WebSocket connection object
        data: The parsed JSON data from the client
    """
    client_id: int = id(websocket)

    # Downgrade to debug level for routine operations
    logger.debug(f"Received 'test' action [client={client_id}]: {data.text}")

    # Example of sending a response back to the client
    try:
        await websocket.send('{"action": "test_response", "status": "ok"}')
    except Exception as e:
        logger.error(f"Failed to send response to client {client_id}: {e}")
