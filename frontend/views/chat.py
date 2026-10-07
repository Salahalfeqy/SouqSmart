import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from components.cards import render_payload
from components.sidebar import new_session, render_sidebar
from services import api

st.markdown(
    """
    <style>
    [data-testid="stChatMessageContent"] p, [data-testid="stChatMessageContent"] li {unicode-bidi: plaintext; text-align: start;}
    [data-testid="stChatMessageContent"] table {font-size: 0.85rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "session_id" not in st.session_state:
    new_session()

render_sidebar()

st.title("Chat")
st.caption("Tell me what you need, your budget in EGP and what matters most. Arabic and English both work.")

EXAMPLES = ["I need a smartphone for gaming and photography", "Best laptop for programming under 50000", "Compare Samsung A56, Xiaomi 14T and iPhone 15", "عاوز سماعة بعزل ضوضاء في حدود 5 آلاف جنيه"]

if not st.session_state.messages:
    st.markdown("**Try one of these:**")
    cols = st.columns(len(EXAMPLES))
    for col, text in zip(cols, EXAMPLES):
        if col.button(text, width="stretch", key=f"ex-{text}"):
            st.session_state.pending = text
            st.rerun()

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🛒" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("payload"):
            render_payload(msg["payload"], key_prefix=f"m{i}-")

prompt = st.chat_input("Type your message...") or st.session_state.pop("pending", None)
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "payload": {}})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🛒"):
        with st.spinner("Searching, comparing and scoring..."):
            try:
                result = api.chat(st.session_state.session_id, prompt)
                reply, payload, meta = result["reply"], result["payload"], result
            except api.ApiError as exc:
                reply, payload, meta = f"Sorry, I couldn't process that: {exc}", {}, None
        st.markdown(reply)
        render_payload(payload, key_prefix="new-")
        if meta:
            tag = "⚡ cached" if meta["cache_hit"] else "fresh"
            st.caption(f"{tag} · {meta['response_time'] * 1000:.0f} ms")
    st.session_state.messages.append({"role": "assistant", "content": reply, "payload": payload})
    st.rerun()
