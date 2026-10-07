import json
import re
import time

import requests

from app.agents.prompts import EXPLANATION_SYSTEM, EXTRACTION_SYSTEM
from app.config import settings

NUMBER_RE = re.compile(r"\d[\d,\.]*")


def enabled() -> bool:
    return bool(settings.llm_api_key)


def chat(messages, json_mode=False, temperature=0.2):
    if not enabled():
        return None
    body = {"model": settings.llm_model, "messages": messages, "temperature": temperature}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    resp = requests.post(
        f"{settings.llm_base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json=body,
        timeout=settings.llm_timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def extract_requirements(message: str):
    try:
        raw = chat([{"role": "system", "content": EXTRACTION_SYSTEM}, {"role": "user", "content": message}], json_mode=True, temperature=0)
        data = json.loads(raw) if raw else None
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def contains_unsafe_numbers(text: str, allowed: set) -> bool:
    for m in NUMBER_RE.findall(text):
        digits = m.replace(",", "").rstrip(".")
        try:
            value = float(digits)
        except ValueError:
            continue
        if value >= 1000 and int(value) not in allowed:
            return True
    return False


def explain(facts: dict, user_message: str, allowed_prices: set):
    started = time.perf_counter()
    try:
        text = chat(
            [
                {"role": "system", "content": EXPLANATION_SYSTEM},
                {"role": "user", "content": f"User message: {user_message}\nFacts: {json.dumps(facts, ensure_ascii=False)}"},
            ]
        )
    except Exception:
        return None, (time.perf_counter() - started) * 1000
    elapsed = (time.perf_counter() - started) * 1000
    if not text or contains_unsafe_numbers(text, allowed_prices):
        return None, elapsed
    if re.search(r"egp|جنيه|l\.?e\b", text, re.I) and NUMBER_RE.search(text):
        return None, elapsed
    return text.strip(), elapsed
