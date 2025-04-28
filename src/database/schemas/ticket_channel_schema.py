from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class TicketChannelSchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    category_id: PositiveInt | None = Field(default=None)

    model_config = ConfigDict(from_attributes=True)
