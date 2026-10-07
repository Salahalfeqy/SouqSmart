import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="SouqSmart", page_icon="🛒", layout="wide")

navigation = st.navigation(
    [
        st.Page("views/chat.py", title="Chat", icon="💬", default=True),
        st.Page("views/dashboard.py", title="Dashboard", icon="📊", url_path="dashboard"),
    ]
)
navigation.run()
