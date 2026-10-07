import os

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
BASE = f"{API_URL}/api/v1"
TIMEOUT = float(os.getenv("API_TIMEOUT", "60"))


class ApiError(Exception):
    pass


def _request(method, path, **kwargs):
    try:
        resp = requests.request(method, f"{BASE}{path}", timeout=TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError as exc:
        raise ApiError("Cannot reach the SouqSmart API. Make sure the backend is running.") from exc
    except requests.exceptions.Timeout as exc:
        raise ApiError("The request timed out. Please try again.") from exc
    except requests.exceptions.HTTPError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", "")
        except ValueError:
            pass
        raise ApiError(f"API error {exc.response.status_code}: {detail}") from exc


def chat(session_id, message):
    return _request("POST", "/chat", json={"session_id": session_id, "message": message})


def messages(session_id):
    return _request("GET", f"/sessions/{session_id}/messages")


def sessions():
    return _request("GET", "/sessions")


def preferences(session_id):
    return _request("GET", f"/preferences/{session_id}")


def save_preferences(session_id, **data):
    return _request("POST", "/preferences", json={"session_id": session_id, **data})


def reset_preferences(session_id):
    return _request("DELETE", f"/preferences/{session_id}")


def analytics():
    return _request("GET", "/analytics")


def clear_cache():
    return _request("POST", "/analytics/cache/clear")
