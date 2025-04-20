from pydantic import BaseModel, Field


class AuthenticateSchema(BaseModel):
    action: str = Field(default="authenticate")
    password: str
    server_list: list[str]
