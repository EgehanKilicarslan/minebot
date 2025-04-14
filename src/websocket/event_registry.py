from logging import Logger
from typing import Callable

from debug import get_logger

logger: Logger = get_logger(__name__)

# Dictionary to store event handlers
event_handlers: dict[str, Callable] = {}


def websocket_event(event_name: str, should_load_hook: bool = True) -> Callable:
    """
    Decorator function to register event handlers.

    Args:
        event_name (str): The name of the event to register the handler for.
        should_load_hook (bool, optional): Flag to control if the handler should be registered.
            Defaults to True.

    Returns:
        Callable: A decorator function that registers the decorated function as an event handler.
    """

    def decorator(func: Callable) -> Callable:
        if should_load_hook:
            if event_name in event_handlers:
                logger.warning(f"Overriding existing handler for WebSocket event: {event_name}")

            event_handlers[event_name] = func

            # Only log at debug level instead of info to reduce noise
            logger.debug(
                f"WebSocket event '{event_name}' registered: {func.__module__}.{func.__name__}"
            )
        return func

    return decorator
