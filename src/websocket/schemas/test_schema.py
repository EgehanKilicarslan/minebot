from websocket.schemas import BaseSchema


class TestSchema(BaseSchema, action="test"):
    text: str
