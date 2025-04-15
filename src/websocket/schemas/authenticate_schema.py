from pydantic import BaseModel, Field


class AuthenticateSchema(BaseModel):
    action: str = Field(default="authenticate")
    username: str
    password: str
