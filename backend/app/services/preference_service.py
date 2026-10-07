from sqlalchemy.orm import Session

from app.database.repositories import UserRepository


def pref_to_dict(pref) -> dict:
    if pref is None:
        return {"budget": None, "preferred_brands": [], "preferred_categories": [], "must_have_features": [], "priority_features": []}
    return {
        "budget": pref.budget,
        "preferred_brands": list(pref.preferred_brands or []),
        "preferred_categories": list(pref.preferred_categories or []),
        "must_have_features": list(pref.must_have_features or []),
        "priority_features": list(pref.priority_features or []),
    }


def unique(items):
    return list(dict.fromkeys(items))


class PreferenceService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def get(self, session_id: str) -> dict:
        user = self.users.get_or_create(session_id)
        return pref_to_dict(self.users.get_preferences(user.id))

    def save(self, session_id: str, data: dict) -> dict:
        user = self.users.get_or_create(session_id)
        current = pref_to_dict(self.users.get_preferences(user.id))
        clean = {k: v for k, v in data.items() if k in current and v is not None}
        current.update(clean)
        self.users.save_preferences(user.id, current)
        return current

    def merge_requirements(self, session_id: str, req) -> dict:
        user = self.users.get_or_create(session_id)
        current = pref_to_dict(self.users.get_preferences(user.id))
        if req.budget is not None:
            current["budget"] = req.budget
        if req.brands and req.intent in {"recommend", "shopping_list"}:
            current["preferred_brands"] = unique(req.brands)
        if req.categories:
            current["preferred_categories"] = unique(req.categories)
        if req.priorities:
            current["priority_features"] = unique(req.priorities)
        if req.must_have:
            current["must_have_features"] = unique(current["must_have_features"] + req.must_have)
        if req.reset:
            current = pref_to_dict(None)
        self.users.save_preferences(user.id, current)
        return current

    def reset(self, session_id: str) -> dict:
        user = self.users.get_or_create(session_id)
        empty = pref_to_dict(None)
        self.users.save_preferences(user.id, empty)
        return empty
