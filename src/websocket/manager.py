import asyncio
from logging import Logger

import websockets

from debug import get_logger
from websocket import handle_connection
from websocket.event_registry import event_handlers

logger: Logger = get_logger(__name__)


class WebSocketManager:
    """
    Manager class for the WebSocket server.
    Handles initialization, running, and graceful shutdown of the WebSocket server.
    """

    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        """
        Initialize the WebSocket manager with host and port configuration.

        Args:
            host (str): Hostname to bind the server to. Defaults to "localhost".
            port (int): Port number to run the server on. Defaults to 8765.
        """
        self.host: str = host
        self.port: int = port
        self.server = None
        self._task = None
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """
        Start the WebSocket server as an asyncio task.

        Returns:
            None
        """
        if self._task is not None:
            logger.warning("WebSocket server already running")
            return

        # Import events here to avoid circular imports
        # This triggers registration of event handlers
        try:
            # Downgraded to debug
            logger.debug("Loading WebSocket event handlers")
            import websocket.events  # noqa: F401

            # Keep this as info since it's a summary of handlers
            logger.info(
                f"Starting WebSocket server with {len(event_handlers)} registered event handlers"
            )
        except Exception as e:
            logger.error(f"Failed to load WebSocket event handlers: {e}", exc_info=True)
            return

        self._task = asyncio.create_task(self._run_server())

    async def _run_server(self) -> None:
        """
        Internal method that runs the actual server.

        Returns:
            None
        """
        try:
            self.server = await websockets.serve(
                handle_connection,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5,
            )

            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")

            # Run until shutdown event is set
            await self._shutdown_event.wait()

        except OSError as e:
            logger.critical(f"Failed to start WebSocket server: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error in WebSocket server: {e}", exc_info=True)
            raise

    async def stop(self) -> None:
        """
        Stop the WebSocket server gracefully.

        Returns:
            None
        """
        if not self._task:
            return

        logger.info("Shutting down WebSocket server")

        # Signal the server to stop
        self._shutdown_event.set()

        # Close the server if it exists
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Cancel the task if it's running
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                logger.warning("Forced WebSocket server task cancellation")
            finally:
                self._task = None
                self.server = None
                self._shutdown_event.clear()
                logger.info("WebSocket server shutdown complete")
