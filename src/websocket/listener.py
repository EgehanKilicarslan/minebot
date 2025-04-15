import json
from logging import Logger
from typing import Any, Callable

from pydantic import BaseModel, ValidationError
from websockets import ServerConnection

from debug import get_logger
from websocket import action_handlers

logger: Logger = get_logger(__name__)


async def handle_connection(websocket: ServerConnection) -> None:
    """
    Handle an incoming WebSocket connection.

    This function processes messages from connected clients, dispatches them
    to the appropriate action handler based on the action type in the message.

    Args:
        websocket: The WebSocket connection object.
    """
    client_id = id(websocket)
    # Keep connections at debug level, not info
    logger.debug(f"WebSocket connection established [id={client_id}]")

    try:
        async for message in websocket:
            try:
                data: dict[str, Any] = json.loads(message)
                action: Any | None = data.get("action")

                if not action:
                    logger.warning(f"Received message without action type [client={client_id}]")
                    continue

                # Use debug level for routine message handling
                logger.debug(f"Received '{action}' action [client={client_id}]")

                action_info: dict[str, Any] | None = action_handlers.get(action)
                if action_info:
                    handler: Callable | None = action_info.get("handler")
                    schema: type[BaseModel] | None = action_info.get("schema")

                    if handler and schema:
                        try:
                            await handler(websocket, schema(**data))
                        except ValidationError as e:
                            logger.error(
                                f"Validation error for action '{action}' [client={client_id}]: {e}"
                            )
                            continue

                else:
                    logger.warning(f"No handler registered for action: {action}")

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
