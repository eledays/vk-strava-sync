import datetime
from sqlalchemy import String, Boolean, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vk_id: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)

    strava_cookies: Mapped[str] = mapped_column(Text, nullable=True)

    # Мета
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} vk_id={self.vk_id}>"