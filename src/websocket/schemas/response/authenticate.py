from ..base import BaseSchema


class AuthenticateSchema(BaseSchema, action="authenticate"):
    password: str
    server_list: list[str]
