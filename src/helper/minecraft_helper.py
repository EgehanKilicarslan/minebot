import asyncio

from data_types import TimedSet
from websocket import WebSocketManager
from websocket.schemas import PlayerStatusCheckSchema

ONLINE_PLAYERS: TimedSet = TimedSet[str](10)


class MinecraftHelper:
    @staticmethod
    async def check_player_status(username: str | None = None, uuid: str | None = None) -> bool:
        if not (username or uuid) or (username and uuid):
            raise ValueError("Exactly one of 'username' or 'uuid' must be provided.")

        await WebSocketManager.send_message(PlayerStatusCheckSchema(username=username, uuid=uuid))
        await asyncio.sleep(1)

        return ONLINE_PLAYERS.contains(username or uuid)
