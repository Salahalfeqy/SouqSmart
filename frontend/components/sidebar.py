import uuid
from datetime import date, datetime

import streamlit as st

from services import api


def new_session():
    st.session_state.session_id = uuid.uuid4().hex[:12]
    st.session_state.messages = []
    st.session_state.loaded = True


def load_session(session_id):
    st.session_state.session_id = session_id
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"], "payload": m.get("payload") or {}} for m in api.messages(session_id)
    ]
    st.session_state.loaded = True


def group_label(ts):
    day = datetime.fromisoformat(ts.replace("Z", "+00:00")).date()
    delta = (date.today() - day).days
    if delta <= 0:
        return "Today"
    if delta == 1:
        return "Yesterday"
    return "Earlier"


def render_history():
    st.subheader("Previous conversations")
    try:
        items = api.sessions()
    except api.ApiError as exc:
        st.caption(str(exc))
        return
    if not items:
        st.caption("No conversations yet.")
        return
    groups = {"Today": [], "Yesterday": [], "Earlier": []}
    for it in items:
        groups[group_label(it["last_activity"])].append(it)
    for label, rows in groups.items():
        if not rows:
            continue
        st.caption(label)
        for it in rows:
            active = it["session_id"] == st.session_state.get("session_id")
            if st.button(("▸ " if active else "") + it["title"], key=f"hist-{it['session_id']}", width="stretch"):
                load_session(it["session_id"])
                st.rerun()


def render_preferences():
    st.subheader("Remembered preferences")
    try:
        prefs = api.preferences(st.session_state.session_id)
    except api.ApiError as exc:
        st.caption(str(exc))
        return
    rows = []
    if prefs["budget"]:
        rows.append(f"Budget: **{int(prefs['budget']):,} EGP**")
    if prefs["preferred_categories"]:
        rows.append("Category: " + ", ".join(prefs["preferred_categories"]))
    if prefs["preferred_brands"]:
        rows.append("Brands: " + ", ".join(prefs["preferred_brands"]))
    if prefs["priority_features"]:
        rows.append("Priorities: " + ", ".join(prefs["priority_features"]))
    if prefs["must_have_features"]:
        rows.append("Must-have: " + ", ".join(prefs["must_have_features"]))
    if rows:
        for r in rows:
            st.markdown(f"- {r}")
        if st.button("Clear preferences", width="stretch"):
            api.reset_preferences(st.session_state.session_id)
            st.rerun()
    else:
        st.caption("Nothing saved yet. Tell me your budget, brands or priorities.")


def render_sidebar():
    with st.sidebar:
        st.title("SouqSmart")
        st.caption("AI shopping & price comparison assistant")
        if st.button("＋ New chat", width="stretch", type="primary"):
            new_session()
            st.rerun()
        render_preferences()
        st.divider()
        render_history()
