from model import MessageType

from ..base import ServerBaseSchema


class SendServerMessageSchema(ServerBaseSchema, action="send-server-message"):
    message_type: MessageType
    message: str
