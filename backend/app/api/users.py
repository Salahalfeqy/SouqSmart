from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.database.repositories import UserRepository
from app.schemas.schemas import MessageOut, PreferencesIn, PreferencesOut, SessionOut
from app.services.preference_service import PreferenceService

router = APIRouter(tags=["users"])


@router.get("/preferences/{session_id}", response_model=PreferencesOut)
def get_preferences(session_id: str, db: Session = Depends(db_session)):
    return {"session_id": session_id, **PreferenceService(db).get(session_id)}


@router.post("/preferences", response_model=PreferencesOut)
def save_preferences(body: PreferencesIn, db: Session = Depends(db_session)):
    data = body.model_dump(exclude={"session_id"}, exclude_none=True)
    return {"session_id": body.session_id, **PreferenceService(db).save(body.session_id, data)}


@router.delete("/preferences/{session_id}", response_model=PreferencesOut)
def reset_preferences(session_id: str, db: Session = Depends(db_session)):
    return {"session_id": session_id, **PreferenceService(db).reset(session_id)}


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(limit: int = 50, db: Session = Depends(db_session)):
    return UserRepository(db).sessions(min(max(limit, 1), 200))


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
def session_messages(session_id: str, db: Session = Depends(db_session)):
    repo = UserRepository(db)
    user = repo.get_or_create(session_id)
    return repo.messages(user.id)
