from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt


class TemporaryActionSchema(BaseModel):
    id: PositiveInt | None = Field(default=None)
    user_id: PositiveInt
    punishment_type: str = Field(max_length=50)
    expires_at: datetime
    refresh_at: datetime | None = Field(default=None)

    class Config:
        from_attributes = True
