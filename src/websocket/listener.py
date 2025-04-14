import json
from logging import Logger

from debug import get_logger
from websocket.event_registry import event_handlers

logger: Logger = get_logger(__name__)


async def handle_connection(websocket):
    """
    Handle an incoming WebSocket connection.

    This function processes messages from connected clients, dispatches them
    to the appropriate event handler based on the event type in the message.

    Args:
        websocket: The WebSocket connection object.
    """
    client_id = id(websocket)
    # Keep connections at debug level, not info
    logger.debug(f"WebSocket connection established [id={client_id}]")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                event = data.get("event")

                if not event:
                    logger.warning(f"Received message without event type [client={client_id}]")
                    continue

                # Use debug level for routine message handling
                logger.debug(f"Received '{event}' event [client={client_id}]")

                handler = event_handlers.get(event)
                if handler:
                    await handler(websocket, data)
                else:
                    logger.warning(f"No handler registered for event: {event}")

            except json.JSONDecodeError:
                logger.error(f"Received invalid JSON [client={client_id}]: {message[:100]}")
            except Exception as e:
                logger.error(
                    f"Error processing message [client={client_id}]: {str(e)}", exc_info=True
                )

    except Exception as e:
        logger.error(f"WebSocket connection error [client={client_id}]: {str(e)}", exc_info=True)
    finally:
        # Keep connections at debug level, not info
        logger.debug(f"WebSocket connection closed [id={client_id}]")
