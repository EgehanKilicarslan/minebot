import asyncio
from logging import Logger

import lightbulb
import websockets

from debug import get_logger
from model import WebSocketKeys
from settings import Settings

from .action_registry import action_handlers
from .listener import handle_connection

logger: Logger = get_logger(__name__)


class WebSocketServer:
    """
    Manager class for the WebSocket server.
    Handles initialization, running, and graceful shutdown of the WebSocket server.
    """

    def __init__(self, client: lightbulb.Client) -> None:
        """
        Initialize the WebSocket manager with host and port configuration.

        Sets up the server configuration and determines if the WebSocket server
        should be enabled based on settings availability.
        """
        self.host: str | None = Settings.get(WebSocketKeys.HOST)
        self.port: int | None = Settings.get(WebSocketKeys.PORT)
        self.client: lightbulb.Client = client
        self.server = None
        self._task = None
        self._shutdown_event = asyncio.Event()

        if self.host is None or self.port is None:
            logger.info("WebSocket server is disabled (host or port not set)")
            self.is_enabled = False
        else:
            self.is_enabled = True

    async def start(self) -> None:
        """
        Start the WebSocket server as an asyncio task.

        Returns:
            None
        """
        if not self.is_enabled:
            return

        if self._task is not None:
            logger.warning("WebSocket server already running")
            return

        logger.info("Starting WebSocket server")

        # Import actionss here to avoid circular imports
        # This triggers registration of action handlers
        try:
            # Downgraded to debug
            logger.debug("Loading WebSocket action handlers")
            import websocket.actions.event  # noqa: F401
            import websocket.actions.request  # noqa: F401
            import websocket.actions.response  # noqa: F401

            # Keep this as info since it's a summary of handlers
            logger.info(
                f"Starting WebSocket server with {len(action_handlers)} registered action handlers"
            )
        except Exception as e:
            logger.error(f"Failed to load WebSocket action handlers: {e}", exc_info=True)
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
                lambda websocket: handle_connection(websocket, self.client),
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
        if not self.is_enabled or not self._task:
            return

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
