import streamlit as st

ICONS = {"smartphone": "📱", "laptop": "💻", "headphones": "🎧"}
BREAKDOWN_LABELS = {"price": "Price (30%)", "performance": "Performance (25%)", "specs": "Specifications (20%)", "preferences": "Preferences (15%)", "reviews": "Reviews (10%)"}


def stars(rating):
    full = int(round(rating))
    return "★" * full + "☆" * (5 - full)


def product_card(card, winner=False, key=""):
    with st.container(border=True):
        icon = ICONS.get(card["category"], "🛒")
        head = f"{icon} **{card['name']}**"
        if winner:
            head += "  `Top pick`"
        st.markdown(head)
        st.caption(card["brand"])
        if card["price_verified"]:
            st.markdown(f"### {card['price_text']}")
        else:
            st.markdown(f"**{card['price_text']}**")
        if not card["available"]:
            st.warning("Out of stock")
        st.caption(f"{stars(card['rating'])} {card['rating']}/5")
        if card.get("value_score") is not None:
            st.progress(min(max(card["value_score"] / 100, 0.0), 1.0), text=f"Value score {card['value_score']}/100")
        else:
            st.caption("Value score unavailable")
        specs = list(card["key_specs"].items())[:6]
        if specs:
            st.markdown("\n".join(f"- {label}: **{value}**" for label, value in specs))
        if card["reasons"]:
            st.markdown("**Why:** " + " · ".join(card["reasons"]))
        if card.get("score_breakdown"):
            with st.expander("Score breakdown"):
                for k, v in card["score_breakdown"].items():
                    st.progress(min(max(v / 100, 0.0), 1.0), text=f"{BREAKDOWN_LABELS.get(k, k)}: {v}")


def render_payload(payload, key_prefix=""):
    cards = payload.get("cards") or []
    if not cards or payload.get("type") in {"message", "error"}:
        return
    if payload.get("type") == "reviews":
        return
    cols = st.columns(min(len(cards), 3))
    for i, card in enumerate(cards):
        with cols[i % len(cols)]:
            product_card(card, winner=card["id"] == payload.get("winner_id"), key=f"{key_prefix}{card['id']}")
