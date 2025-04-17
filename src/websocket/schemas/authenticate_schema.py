from pydantic import BaseModel, Field, model_validator


class AuthenticateSchema(BaseModel):
    action: str = Field(default="authenticate")
    server_type: str = Field(..., pattern=r"^(bukkit|proxy)$")
    password: str
    server_list: list[str] | None = Field(
        default=None, description="List of servers under the proxy."
    )

    @model_validator(mode="after")
    def check_server_list(self) -> "AuthenticateSchema":
        if self.server_type == "proxy" and not self.server_list:
            raise ValueError("server_list must be provided when server_type is 'proxy'")
        return self
