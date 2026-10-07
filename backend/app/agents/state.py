import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, TypedDict

from sqlalchemy.orm import Session

from app.agents.tools import AgentTools
from app.services.cache_service import CacheService
from app.services.product_service import ProductService


class AgentState(TypedDict, total=False):
    session_id: str
    message: str
    language: str
    requirements: dict
    preferences: dict
    intent: str
    category: str | None
    product_ids: list
    candidates: list
    ranked: list
    comparison: dict
    reviews: dict
    shopping_list: dict
    notes: Annotated[list, operator.add]
    trace: Annotated[list, operator.add]
    reply: str
    payload: dict
    cache_key: str | None
    cache_hit: bool
    error: str | None
    clarify: str | None


@dataclass
class AgentContext:
    db: Session
    tools: AgentTools
    products: ProductService
    cache: CacheService
    timings: dict = field(default_factory=dict)
    extras: dict = field(default_factory=dict)
