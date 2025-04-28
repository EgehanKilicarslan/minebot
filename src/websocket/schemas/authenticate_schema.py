from .base_schema import BaseSchema


class AuthenticateSchema(BaseSchema, action="authenticate"):
    password: str
    server_list: list[str]
