from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator


class UserSchema(BaseModel):
    id: PositiveInt
    locale: str
    minecraft_username: str | None = Field(default=None, max_length=16)
    minecraft_uuid: str | None = Field(default=None, max_length=36)
    reward_inventory: dict[str, list[str]] | None = Field(default=None)

    @field_validator("reward_inventory")
    @classmethod
    def validate_reward_inventory(
        cls, v: dict[str, list[str]] | None
    ) -> dict[str, list[str]] | None:
        if v is None:
            return v

        # Check if each key in the inventory is a valid Minecraft server
        from helper import MINECRAFT_SERVERS

        # If MINECRAFT_SERVERS is empty or None, skip validation
        if not MINECRAFT_SERVERS:
            return v

        invalid_keys: list[str] = [key for key in v.keys() if key not in MINECRAFT_SERVERS]
        if invalid_keys:
            raise ValueError(
                f"Invalid server keys: {invalid_keys}. Allowed keys are: {MINECRAFT_SERVERS}"
            )

        return v

    model_config = ConfigDict(from_attributes=True)
