import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import api

PALETTE = {"primary": "#2A7F77", "accent": "#E07A5F", "muted": "#9AA5B1"}

st.title("Analytics dashboard")

top = st.columns([6, 1, 1])
if top[1].button("Refresh", width="stretch"):
    st.rerun()
if top[2].button("Clear cache", width="stretch"):
    try:
        api.clear_cache()
        st.toast("Cache cleared")
    except api.ApiError as exc:
        st.error(str(exc))

try:
    data = api.analytics()
except api.ApiError as exc:
    st.error(str(exc))
    st.stop()

cache = data["cache"]
avg = data["avg_response_time_s"]
row1 = st.columns(3)
row1[0].metric("Total searches", data["total_searches"])
row1[1].metric("Total comparisons", data["total_comparisons"])
row1[2].metric("Cache hit rate", f"{cache['hit_rate']}%")
row2 = st.columns(3)
row2[0].metric("Avg response time", f"{avg * 1000:.0f} ms" if avg is not None else "n/a")
row2[1].metric("Popular category", (data["popular_category"] or "n/a").capitalize())
row2[2].metric("Popular brand", data["popular_brand"] or "n/a")

if data["total_searches"] == 0:
    st.info("No activity yet. Chat with SouqSmart and the numbers will appear here.")
    st.stop()


def bar(d, title, horizontal=False, color=PALETTE["primary"]):
    df = pd.DataFrame({"name": list(d.keys()), "count": list(d.values())})
    if df.empty:
        st.caption(f"{title}: no data yet")
        return
    df = df.sort_values("count", ascending=horizontal)
    fig = px.bar(df, x="count" if horizontal else "name", y="name" if horizontal else "count", orientation="h" if horizontal else "v", title=title, color_discrete_sequence=[color])
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title=None, yaxis_title=None, height=320)
    st.plotly_chart(fig, width="stretch")


c1, c2 = st.columns(2)
with c1:
    bar(data["categories"], "Most searched categories")
with c2:
    bar(data["brands"], "Popular brands")

c3, c4 = st.columns(2)
with c3:
    bar(data["most_compared_products"], "Most compared products", horizontal=True, color=PALETTE["accent"])
with c4:
    bar(data["top_recommended_products"], "Most recommended products", horizontal=True)

st.subheader("Cache performance")
c5, c6 = st.columns(2)
with c5:
    df = pd.DataFrame({"Requests": ["Cache hits", "Cache misses"], "count": [cache["hits"], cache["misses"]]})
    fig = px.bar(df, x="Requests", y="count", title=f"Hits vs misses (backend: {cache['backend']}, TTL {cache['ttl_seconds']}s)", color="Requests",
                 color_discrete_map={"Cache hits": PALETTE["primary"], "Cache misses": PALETTE["muted"]})
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0), height=320, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, width="stretch")
with c6:
    cached, uncached = cache["avg_cached_response_s"], cache["avg_uncached_response_s"]
    df = pd.DataFrame({"Type": ["Cached", "Uncached"], "ms": [(cached or 0) * 1000, (uncached or 0) * 1000]})
    fig = px.bar(df, x="Type", y="ms", title="Average response time (ms)", color="Type", color_discrete_map={"Cached": PALETTE["primary"], "Uncached": PALETTE["muted"]})
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0), height=320, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, width="stretch")

st.subheader("Response time per request")
rt = pd.DataFrame(data["response_times"])
if not rt.empty:
    rt["ms"] = rt["seconds"] * 1000
    rt["request"] = range(1, len(rt) + 1)
    rt["type"] = rt["cache_hit"].map({True: "Cached", False: "Uncached"})
    fig = px.scatter(rt, x="request", y="ms", color="type", color_discrete_map={"Cached": PALETTE["primary"], "Uncached": PALETTE["muted"]})
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=320, xaxis_title="Request #", yaxis_title="ms")
    st.plotly_chart(fig, width="stretch")

lat = data["component_latency_ms"]
st.subheader("Component latency (since API start)")
l = st.columns(4)
for col, (label, key) in zip(l, [("Cached request", "avg_cached_ms"), ("Uncached request", "avg_uncached_ms"), ("RAG retrieval", "avg_rag_ms"), ("LLM generation", "avg_llm_ms")]):
    col.metric(label, f"{lat[key]} ms" if lat[key] is not None else "n/a")

if data["searches_per_day"]:
    daily = pd.DataFrame({"day": list(data["searches_per_day"].keys()), "searches": list(data["searches_per_day"].values())})
    fig = px.line(daily, x="day", y="searches", markers=True, title="Searches per day", color_discrete_sequence=[PALETTE["primary"]])
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=300, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, width="stretch")
