from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProductOut(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: float | None
    old_price: float | None = None
    price_verified: bool
    description: str = ""
    rating: float
    stock: int
    available: bool
    url: str = ""
    image_url: str = ""
    specs: dict[str, Any] = {}
    review_count: int = 0
    review_avg: float | None = None


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=300)
    category: str | None = None
    brands: list[str] = []
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    available_only: bool = False
    limit: int = Field(default=20, ge=1, le=100)


class CompareRequest(BaseModel):
    product_ids: list[int] = Field(min_length=1, max_length=6)
    session_id: str | None = None
    budget: float | None = None
    priority_features: list[str] = []
    preferred_brands: list[str] = []


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=1000)

    @field_validator("message")
    @classmethod
    def not_blank(cls, v):
        if not v.strip():
            raise ValueError("message must not be blank")
        return v.strip()


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    payload: dict[str, Any]
    intent: str | None = None
    preferences: dict[str, Any] | None = None
    cache_hit: bool
    response_time: float
    trace: list[str] = []


class PreferencesIn(BaseModel):
    session_id: str = Field(min_length=1, max_length=80)
    budget: float | None = Field(default=None, ge=0)
    preferred_brands: list[str] | None = None
    preferred_categories: list[str] | None = None
    must_have_features: list[str] | None = None
    priority_features: list[str] | None = None


class PreferencesOut(BaseModel):
    session_id: str
    budget: float | None
    preferred_brands: list[str]
    preferred_categories: list[str]
    must_have_features: list[str]
    priority_features: list[str]


class MessageOut(BaseModel):
    role: str
    content: str
    payload: dict[str, Any] | None = None
    created_at: datetime


class SessionOut(BaseModel):
    session_id: str
    title: str
    last_activity: datetime
