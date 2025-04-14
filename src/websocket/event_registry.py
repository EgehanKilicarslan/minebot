from logging import Logger
from typing import Any, Callable

from pydantic import BaseModel

from debug import get_logger

logger: Logger = get_logger(__name__)

# Dictionary to store event handlers
event_handlers: dict[str, dict[str, Any]] = {}


def websocket_event(
    event_name: str, schema: type[BaseModel], should_load_hook: bool = True
) -> Callable:
    """
    Decorator function to register event handlers.

    Args:
        event_name (str): The name of the event to register the handler for.
        schema (type[BaseModel]): The Pydantic model class for validating the event data.
        should_load_hook (bool, optional): Flag to control if the handler should be registered.
            Defaults to True.

    Returns:
        Callable: A decorator function that registers the decorated function as an event handler.
    """

    def decorator(func: Callable) -> Callable:
        if should_load_hook:
            if event_name in event_handlers:
                logger.warning(f"Overriding existing handler for WebSocket event: {event_name}")

            event_handlers[event_name] = {
                "handler": func,
                "schema": schema,
            }

            # Only log at debug level instead of info to reduce noise
            logger.debug(
                f"WebSocket event '{event_name}' registered: {func.__module__}.{func.__name__}"
            )
        return func

    return decorator
