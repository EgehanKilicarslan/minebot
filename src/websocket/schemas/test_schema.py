from pydantic import BaseModel, Field


class TestSchema(BaseModel):
    event: str = Field(default="test")
    text: str
