from websocket.schemas import ServerBaseSchema


class TestSchema(ServerBaseSchema, action="test"):
    text: str
