from pydantic import BaseModel, Field, PositiveInt


class TicketChannelSchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    category_id: PositiveInt | None = Field(default=None)

    class Config:
        from_attributes = True
