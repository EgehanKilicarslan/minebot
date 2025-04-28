from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class UserSchema(BaseModel):
    id: PositiveInt
    locale: str
    minecraftUsername: str | None = Field(default=None, max_length=16)
    minecraftUUID: str | None = Field(default=None, max_length=36)

    model_config = ConfigDict(from_attributes=True)
