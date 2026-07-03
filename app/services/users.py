from app.models.user import User
from app.database import get_session

from logging import getLogger

logger = getLogger(__name__)


def get_or_create_user_by_vk_id(vk_id: int) -> User:
    with get_session() as session:
        user = session.query(User).filter_by(vk_id=vk_id).first()
        if user is None:
            user = User(vk_id=vk_id)
            session.add(user)
            session.commit()
            logger.info(f"Created new user: {user}")
        else:
            logger.info(f"Found existing user: {user}")
        return user


def save_strava_cookies(user_id: int, cookies: str) -> None:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")

        user.strava_cookies = cookies
        session.commit()