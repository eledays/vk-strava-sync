from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Config
from app.models import Base

# Автосоздание директории для SQLite
if Config.DB_URL.startswith("sqlite"):
    db_path = Config.DB_URL.removeprefix("sqlite:///")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    Config.DB_URL,
    echo=Config.DB_ECHO,
    connect_args={"check_same_thread": False} if Config.DB_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def init_db() -> None:
    """Создаёт все таблицы, если их ещё нет."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Возвращает новую сессию. Не забывайте закрывать."""
    return SessionLocal()