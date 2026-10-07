from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.runner import handle_chat
from app.api.deps import cache_service, db_session
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.cache_service import CacheService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(db_session), cache: CacheService = Depends(cache_service)):
    result = handle_chat(db, body.session_id, body.message, cache)
    return ChatResponse(
        session_id=body.session_id,
        reply=result["reply"],
        payload=result["payload"],
        intent=result["intent"],
        preferences=result["preferences"],
        cache_hit=result["cache_hit"],
        response_time=result["response_time"],
        trace=result["trace"],
    )
