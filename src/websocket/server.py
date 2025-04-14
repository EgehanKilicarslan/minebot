from logging import Logger

from debug import get_logger
from websocket.manager import WebSocketManager

logger: Logger = get_logger(__name__)

# Create a singleton instance with configurable settings
websocket_manager = WebSocketManager(
    host="localhost",  # Use 0.0.0.0 for production to accept external connections
    port=8765,
)


# Re-export manager methods as module functions
async def initialize_websocket_server():
    """Start the WebSocket server."""
    # Keep this at info level as it's an important system event
    logger.info("Starting WebSocket server")
    await websocket_manager.start()


async def shutdown_websocket_server():
    """Stop the WebSocket server gracefully."""
    # Keep this at info level as it's an important system event
    logger.info("Stopping WebSocket server")
    await websocket_manager.stop()
