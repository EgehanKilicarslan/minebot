from model import MessageType

from ..base import BaseSchema


class SendGlobalMessageSchema(BaseSchema, action="send-global-message"):
    message_type: MessageType
    message: str
