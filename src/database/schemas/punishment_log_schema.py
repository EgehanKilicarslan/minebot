from datetime import datetime, timezone

from pydantic import BaseModel, Field, PositiveInt


class PunishmentLogSchema(BaseModel):
    id: PositiveInt
    user_id: PositiveInt
    punishment_type: str = Field(max_length=50)
    reason: str
    moderator_id: PositiveInt
    duration: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = Field(default=None)
    source: str = Field(max_length=20)

    class Config:
        from_attributes = True
