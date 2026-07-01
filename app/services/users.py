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
