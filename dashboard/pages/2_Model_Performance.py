import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import load_models, predict_winner
from config import COLORS, DATA_PATH

# ── Session state & data loading ──────────────────────────────────────────────

if "models" not in st.session_state:
    st.session_state["models"] = load_models()

models = st.session_state["models"]


@st.cache_data
def load_and_score(data_path):
    df = pd.read_csv(data_path)

    def get_actual_winner(row):
        return row["home_team"] if row["home_score"] > row["away_score"] else row["away_team"]

    def get_prediction(row):
        try:
            result = predict_winner(row["home_team"], row["away_team"], models)
            return result["predicted_winner"]
        except Exception:
            return None

    df["actual_winner"] = df.apply(get_actual_winner, axis=1)
    df["predicted_winner"] = df.apply(get_prediction, axis=1)
    df["correct"] = df["actual_winner"] == df["predicted_winner"]
    return df


df = load_and_score(DATA_PATH)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.metric-card {
    background: #1a1a1a;
    border: 1px solid #00C853;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.75rem;
    color: #888888;
    letter-spacing: 1.5px;
    margin-top: 6px;
    text-transform: uppercase;
}
.pick-row-a {
    background: #1a1a1a;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.pick-row-b {
    background: #141414;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.pick-game   { color: #FFFFFF; font-weight: 600; font-size: 0.95rem; min-width: 180px; }
.pick-pred   { color: #888888; font-size: 0.85rem; min-width: 140px; }
.pick-actual { color: #FFFFFF; font-size: 0.85rem; min-width: 140px; }
.pick-score  { color: #555555; font-size: 0.8rem; min-width: 80px; text-align: right; }
.pick-result { font-size: 1.1rem; min-width: 28px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("""
<div style="padding: 28px 0 8px 0;">
    <div style="font-size: 2rem; font-weight: 900; color: #FFFFFF;">📊 MODEL PERFORMANCE</div>
    <div style="color: #888888; font-size: 0.95rem; margin-top: 6px;">
        How sharp is the model? Let's find out.
    </div>
</div>
<hr style="border: none; border-top: 1px solid #00C853; margin: 12px 0 28px 0;">
""", unsafe_allow_html=True)

# ── Section 1: Top stats row ──────────────────────────────────────────────────

total = len(df.dropna(subset=["predicted_winner"]))
wins = int(df["correct"].sum())
losses = total - wins
accuracy = wins / total if total else 0

home_wins_actual = int((df["home_score"] > df["away_score"]).sum())
home_win_rate = home_wins_actual / total if total else 0

# Streak: walk from the most recent game backwards
streak_count = 0
streak_type = None
for correct in reversed(df["correct"].dropna().tolist()):
    if streak_type is None:
        streak_type = correct
    if correct == streak_type:
        streak_count += 1
    else:
        break

streak_label = f"🔥 {streak_count} W" if streak_type else f"❄️ {streak_count} L"

col1, col2, col3, col4 = st.columns(4)

for col, value, label in [
    (col1, f"{wins}-{losses}", "RECORD"),
    (col2, f"{accuracy * 100:.1f}%", "ACCURACY"),
    (col3, f"{home_win_rate * 100:.1f}%", "HOME WIN RATE"),
    (col4, streak_label, "CURRENT STREAK"),
]:
    with col:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-value'>{value}</div>"
            f"<div class='metric-label'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)

# ── Section 2: Confusion matrix ───────────────────────────────────────────────

st.markdown(
    "<div style='color:#00C853; font-weight:700; font-size:1.1rem; "
    "letter-spacing:1px; margin-bottom:12px;'>CONFUSION MATRIX</div>",
    unsafe_allow_html=True,
)

scored = df.dropna(subset=["predicted_winner"]).copy()
scored["home_won_actual"] = scored["home_score"] > scored["away_score"]
scored["home_won_pred"] = scored["predicted_winner"] == scored["home_team"]

true_home  = int(( scored["home_won_actual"] &  scored["home_won_pred"]).sum())
false_away = int(( scored["home_won_actual"] & ~scored["home_won_pred"]).sum())
false_home = int((~scored["home_won_actual"] &  scored["home_won_pred"]).sum())
true_away  = int((~scored["home_won_actual"] & ~scored["home_won_pred"]).sum())

z = [[true_home, false_away],
     [false_home, true_away]]

fig = go.Figure(go.Heatmap(
    z=z,
    x=["Predicted: Home Win", "Predicted: Away Win"],
    y=["Actual: Home Win", "Actual: Away Win"],
    text=[[str(v) for v in row] for row in z],
    texttemplate="<b>%{text}</b>",
    textfont={"size": 20, "color": "white"},
    colorscale=[[0, "#FF1744"], [1, "#00C853"]],
    showscale=False,
))

fig.update_layout(
    paper_bgcolor="#0a0a0a",
    plot_bgcolor="#1a1a1a",
    font={"color": "#FFFFFF", "family": "Inter, sans-serif"},
    margin={"t": 20, "b": 20, "l": 20, "r": 20},
    height=320,
    xaxis={"tickfont": {"size": 13}},
    yaxis={"tickfont": {"size": 13}},
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

# ── Section 3: Recent picks feed ──────────────────────────────────────────────

st.markdown(
    "<div style='color:#00C853; font-weight:700; font-size:1.1rem; "
    "letter-spacing:1px; margin-bottom:12px;'>🎯 RECENT PICKS</div>",
    unsafe_allow_html=True,
)

recent = df.dropna(subset=["predicted_winner"]).tail(10).iloc[::-1]

for i, (_, row) in enumerate(recent.iterrows()):
    css_class = "pick-row-a" if i % 2 == 0 else "pick-row-b"
    result_icon = "✅" if row["correct"] else "❌"
    score = f"{int(row['home_score'])}-{int(row['away_score'])}" if "home_score" in row and "away_score" in row else "—"

    st.markdown(
        f"<div class='{css_class}'>"
        f"  <span class='pick-game'>{row['away_team']} vs {row['home_team']}</span>"
        f"  <span class='pick-pred'>Pred: {row['predicted_winner']}</span>"
        f"  <span class='pick-actual'>Actual: {row['actual_winner']}</span>"
        f"  <span class='pick-score'>{score}</span>"
        f"  <span class='pick-result'>{result_icon}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
