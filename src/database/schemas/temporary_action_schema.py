from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class TemporaryActionSchema(BaseModel):
    id: PositiveInt | None = Field(default=None)
    user_id: PositiveInt
    punishment_type: str = Field(max_length=50)
    expires_at: datetime
    refresh_at: datetime | None = Field(default=None)

    model_config = ConfigDict(from_attributes=True)
