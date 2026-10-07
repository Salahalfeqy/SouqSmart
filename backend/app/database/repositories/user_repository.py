from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import ChatMessage, User, UserPreference


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, session_id: str) -> User:
        user = self.db.scalar(select(User).where(User.session_id == session_id))
        if user is None:
            user = User(session_id=session_id)
            self.db.add(user)
            self.db.commit()
        return user

    def get_preferences(self, user_id: int):
        return self.db.scalar(select(UserPreference).where(UserPreference.user_id == user_id))

    def save_preferences(self, user_id: int, data: dict) -> UserPreference:
        pref = self.get_preferences(user_id)
        if pref is None:
            pref = UserPreference(user_id=user_id)
            self.db.add(pref)
        for key in ("budget", "preferred_brands", "preferred_categories", "must_have_features", "priority_features"):
            if key in data:
                setattr(pref, key, data[key])
        self.db.commit()
        return pref

    def add_message(self, user_id: int, role: str, content: str, payload: dict | None = None):
        msg = ChatMessage(user_id=user_id, role=role, content=content, payload=payload)
        self.db.add(msg)
        self.db.commit()
        return msg

    def messages(self, user_id: int, limit: int = 200):
        stmt = select(ChatMessage).where(ChatMessage.user_id == user_id).order_by(ChatMessage.id).limit(limit)
        return list(self.db.scalars(stmt).all())

    def sessions(self, limit: int = 50):
        first_msg = (
            select(ChatMessage.user_id, func.min(ChatMessage.id).label("first_id"), func.max(ChatMessage.created_at).label("last_at"))
            .where(ChatMessage.role == "user")
            .group_by(ChatMessage.user_id)
            .subquery()
        )
        stmt = (
            select(User.session_id, ChatMessage.content, first_msg.c.last_at)
            .join(first_msg, first_msg.c.user_id == User.id)
            .join(ChatMessage, ChatMessage.id == first_msg.c.first_id)
            .order_by(first_msg.c.last_at.desc())
            .limit(limit)
        )
        return [{"session_id": sid, "title": content[:60], "last_activity": last} for sid, content, last in self.db.execute(stmt)]
