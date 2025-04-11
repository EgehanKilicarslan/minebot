from pydantic import BaseModel, PositiveInt


class TicketInfoSchema(BaseModel):
    id: PositiveInt
    channel_id: PositiveInt
    message_id: PositiveInt

    class Config:
        from_attributes = True
