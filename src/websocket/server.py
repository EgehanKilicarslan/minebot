from logging import Logger

from debug import get_logger
from model import WebSocketKeys
from settings import Settings
from websocket.manager import WebSocketManager

logger: Logger = get_logger(__name__)

# Define a lazy-loaded singleton
websocket_manager = None


async def initialize_websocket_server() -> None:
    """Start the WebSocket server."""
    global websocket_manager

    # Initialize the manager if it doesn't exist yet
    if websocket_manager is None:
        websocket_manager = WebSocketManager(
            host=Settings.get(WebSocketKeys.HOST),
            port=Settings.get(WebSocketKeys.PORT),
        )

    await websocket_manager.start()


async def shutdown_websocket_server() -> None:
    """Stop the WebSocket server gracefully."""
    global websocket_manager

    # Only attempt to stop if the manager was initialized
    if websocket_manager is not None:
        await websocket_manager.stop()
