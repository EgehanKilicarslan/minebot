from pydantic import BaseModel, Field, field_validator


class BaseSchema(BaseModel):
    server: str

    def __init_subclass__(cls, action: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.action: str = Field(default=action)
        # Add action to the class's __annotations__ to ensure Pydantic processes it correctly
        cls.__annotations__["action"] = str

    @field_validator("server", mode="after")
    @classmethod
    def validate_server(cls, value: str) -> str:
        # Import inside method to avoid circular import
        from websocket import authenticated_client

        # Check if the server name is in any authenticated client's data
        for client_id, (connection, auth_schema) in authenticated_client.items():
            if value in auth_schema.server_list:
                return value
        raise ValueError(f"Server '{value}' is not authenticated")
