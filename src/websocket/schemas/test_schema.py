from pydantic import BaseModel, Field


class TestSchema(BaseModel):
    action: str = Field(default="test")
    text: str
