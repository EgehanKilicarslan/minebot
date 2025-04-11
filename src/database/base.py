from logging import Logger
from pathlib import Path
from typing import Any, Final

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import declarative_base

from debug import get_logger

logger: Logger = get_logger(__name__)

# Constants for database configuration
DB_PATH: Final[Path] = Path("data").resolve()
DB_FILENAME: Final[str] = "minebot.db"
DATABASE_URL: Final[str] = f"sqlite+aiosqlite:///{DB_PATH / DB_FILENAME}"

# Ensure data directory exists
DB_PATH.mkdir(parents=True, exist_ok=True)

# Create async engine with appropriate pool settings
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

# Create base class for models
Base: Any = declarative_base()
