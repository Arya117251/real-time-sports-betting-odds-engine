import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from utils import load_model, load_bq_data, predict_winner, FEATURES
from config import COLORS

TARGET = "home_win"

# ── Session state & data loading ──────────────────────────────────────────────

if "model" not in st.session_state:
    st.session_state["model"] = load_model()

model = st.session_state["model"]


def load_and_score() -> pd.DataFrame:
    """Fetch gold_game_features from BigQuery and annotate each row with a prediction.

    Adds three columns to the DataFrame:
      - actual_winner:    home_team or away_team derived from the home_win flag.
      - predicted_winner: model prediction using the row's numeric feature values.
      - correct:          True when predicted_winner matches actual_winner.

    Returns the annotated DataFrame.
    """
    df = load_bq_data().copy()

    def get_actual_winner(row):
        """Return the team name that won based on the home_win binary flag."""
        return row["home_team"] if row["home_win"] == 1 else row["away_team"]

    def get_prediction(row):
        """Run predict_winner against the row's feature values; return None on error."""
        try:
            result = predict_winner(row["home_team"], row["away_team"], row, model)
            return result["predicted_winner"]
        except Exception:
            return None

    df["actual_winner"] = df.apply(get_actual_winner, axis=1)
    df["predicted_winner"] = df.apply(get_prediction, axis=1)
    df["correct"] = df["actual_winner"] == df["predicted_winner"]
    return df


df = load_and_score()


def compute_test_metrics(model) -> dict:
    """Reproduce the exact 80/20 train/test split from train_model.py and score the test set.

    Uses the same FEATURES list and random_state=42 as scripts/train_model.py so
    the test rows here are precisely the rows the model never saw during training.
    Returns a dict with:
      - accuracy:     float, held-out test accuracy
      - wins/losses:  int counts of correct/incorrect predictions on the test set
      - true_home, false_away, false_home, true_away: confusion matrix cell counts
      - streak_label: current W/L streak derived from test rows ordered by date
      - home_win_rate: fraction of test games won by the home team
    """
    raw = load_bq_data().dropna(subset=FEATURES + [TARGET]).copy()

    X = raw[FEATURES]
    y = raw[TARGET]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    test_df = raw.loc[X_test.index].copy()
    test_df["y_pred"] = y_pred
    test_df["correct"] = y_pred == y_test.values
    test_df = test_df.sort_values("date")

    wins   = int(test_df["correct"].sum())
    losses = len(test_df) - wins

    # Confusion matrix cells: home = 1, away = 0
    actual_home = test_df[TARGET] == 1
    pred_home   = test_df["y_pred"] == 1
    true_home   = int(( actual_home &  pred_home).sum())
    false_away  = int(( actual_home & ~pred_home).sum())
    false_home  = int((~actual_home &  pred_home).sum())
    true_away   = int((~actual_home & ~pred_home).sum())

    # Current streak (walk test rows from most recent backward)
    streak_count, streak_type = 0, None
    for correct in reversed(test_df["correct"].tolist()):
        if streak_type is None:
            streak_type = correct
        if correct == streak_type:
            streak_count += 1
        else:
            break
    streak_label = f"🔥 {streak_count} W" if streak_type else f"❄️ {streak_count} L"

    home_win_rate = float(test_df[TARGET].mean())

    return dict(
        accuracy=acc,
        wins=wins,
        losses=losses,
        true_home=true_home,
        false_away=false_away,
        false_home=false_home,
        true_away=true_away,
        streak_label=streak_label,
        home_win_rate=home_win_rate,
        total=len(test_df),
    )


metrics = compute_test_metrics(model)

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

col1, col2, col3, col4 = st.columns(4)

for col, value, label in [
    (col1, f"{metrics['wins']}-{metrics['losses']}", "RECORD"),
    (col2, f"{metrics['accuracy'] * 100:.1f}%", "TEST ACCURACY"),
    (col3, f"{metrics['home_win_rate'] * 100:.1f}%", "HOME WIN RATE"),
    (col4, metrics["streak_label"], "CURRENT STREAK"),
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

true_home  = metrics["true_home"]
false_away = metrics["false_away"]
false_home = metrics["false_home"]
true_away  = metrics["true_away"]

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

home_pred_rate = (true_home + false_home) / metrics["total"] if metrics["total"] else 0
st.markdown(
    f"<div style='background:#111111; border-left:3px solid #444444; border-radius:6px; "
    f"padding:12px 16px; color:#888888; font-size:0.82rem; line-height:1.6;'>"
    f"<span style='color:#FFFFFF; font-weight:600;'>Home-win bias:</span> "
    f"The model predicted a home win in <span style='color:#FFFFFF;'>"
    f"{home_pred_rate * 100:.0f}%</span> of test games, compared to an actual home win rate of "
    f"<span style='color:#FFFFFF;'>{metrics['home_win_rate'] * 100:.0f}%</span>. "
    f"This reflects the genuine home-court advantage in the training data — the model learns that "
    f"home teams win more often and leans toward that prediction. As a result, it has stronger "
    f"recall for home wins (true home: <span style='color:#00C853;'>{true_home}</span>) "
    f"but misclassifies more away wins as home wins "
    f"(false home: <span style='color:#FF1744;'>{false_home}</span>)."
    f"</div>",
    unsafe_allow_html=True,
)

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
