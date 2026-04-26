import streamlit as st
from config import COLORS

st.set_page_config(
    page_title="HouseAlwaysWins | NBA Predictions",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0a;
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background-color: #111111;
}

.bet-card {
    background: #1a1a1a;
    border: 1px solid #00C853;
    border-radius: 12px;
    padding: 24px;
}

.stButton > button {
    background: #00C853;
    color: #000000;
    font-weight: 700;
    border-radius: 8px;
    padding: 12px 28px;
    border: none;
}

.stButton > button:hover {
    box-shadow: 0 0 16px #00C85388;
}

.block-container {
    padding-top: 0rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    background: #0a0a0a;
    border-bottom: 2px solid #00C853;
    padding: 40px 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
">
    <div>
        <div style="font-size: 3rem; font-weight: 900; letter-spacing: -1px; line-height: 1.1;">
            🏀 HOUSE <span style="color: #00C853;">ALWAYS</span> WINS
        </div>
        <div style="font-style: italic; color: #888888; margin-top: 10px; font-size: 1.1rem;">
            You won't beat it. But we'll tell you the odds.
        </div>
    </div>
    <div style="
        color: #444444;
        font-size: 0.85rem;
        border: 1px dashed #333333;
        padding: 24px 32px;
        border-radius: 8px;
        text-align: center;
    ">
        [ player image goes here ]
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        "<div style='font-weight: 700; color: #00C853; font-size: 1.2rem;'>HouseAlwaysWins 🏀</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color: #888888; font-size: 0.85rem; margin-top: 4px;'>Beat the line. Trust the model.</div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.page_link("pages/1_Live_Predictions.py", label="Live Predictions", icon="🔴")
    st.page_link("pages/2_Model_Performance.py", label="Model Performance", icon="📊")
    st.page_link("pages/3_Data_Explorer.py", label="Data Explorer", icon="🗂️")
    st.divider()
    st.markdown(
        "<div style='color: #555555; font-size: 0.75rem;'>Model accuracy: 61.4% | 218 games trained</div>",
        unsafe_allow_html=True,
    )
