from pydantic import BaseModel, Field, PositiveInt, field_validator


class SettingsSchema(BaseModel):
    """Settings model with validation."""

    class Secret(BaseModel):
        token: str = Field(..., title="Bot Token", description="Discord bot token")
        default_guild: PositiveInt = Field(
            ..., title="Default Guild ID", description="Default guild ID for the bot"
        )

        @field_validator("token")
        @classmethod
        def validate_token(cls, v: str) -> str:
            if not v.strip():
                raise ValueError("Token cannot be empty or whitespace")
            return v

    class Database(BaseModel):
        url: str = Field(..., title="Database URL", description="Database connection URL")

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            import re

            if not v.strip():
                raise ValueError("Database URL cannot be empty or whitespace")

            patterns: dict[str, str] = {
                "sqlite+aiosqlite://": r"sqlite\+aiosqlite:///.*",
                "mysql+aiomysql://": r"mysql\+aiomysql://[^:]+:.*@[^:]+:[0-9]+/[^/]+",
                "postgresql+asyncpg://": r"postgresql\+asyncpg://[^:]+:.*@[^:]+:[0-9]+/[^/]+",
            }

            for prefix, pattern in patterns.items():
                if v.startswith(prefix):
                    if not re.match(pattern, v):
                        raise ValueError(f"{prefix} URL must follow the correct format.")
                    return v

            raise ValueError(
                "Invalid database URL format. Supported formats are: "
                "sqlite+aiosqlite:///, mysql+aiomysql://, postgresql+asyncpg://"
            )

    secret: Secret
    database: Database


class LocalizationSchema(BaseModel):
    """Localization model with validation."""

    locale: str = Field(..., title="Locale", description="Language locale")

    class Ban(BaseModel):
        class Command(BaseModel):
            label: str = Field(..., title="Label", description="Command label")
            description: str = Field(..., title="Description", description="Command description")

            class Options(BaseModel):
                class User(BaseModel):
                    label: str = Field(..., title="Label", description="User label")
                    description: str = Field(
                        ..., title="Description", description="User description"
                    )

                class Duration(BaseModel):
                    label: str = Field(..., title="Label", description="Duration label")
                    description: str = Field(
                        ..., title="Description", description="Duration description"
                    )

                class Reason(BaseModel):
                    label: str = Field(..., title="Label", description="Reason label")
                    description: str = Field(
                        ..., title="Description", description="Reason description"
                    )

                user: User
                duration: Duration
                reason: Reason

            options: Options

        class Messages(BaseModel):
            class User(BaseModel):
                success: str = Field(..., title="Success", description="Success message")

            user: User

        command: Command
        messages: Messages

    class Error(BaseModel):
        title: str = Field(..., title="Title", description="Error title")
        unknown: str = Field(..., title="Unknown", description="Unknown error message")

    ban: Ban
    error: Error
