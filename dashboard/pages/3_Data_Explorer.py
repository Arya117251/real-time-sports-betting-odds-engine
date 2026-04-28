import streamlit as st
import pandas as pd
from utils import load_bq_data
from config import COLORS

# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
    """Fetch gold_game_features from BigQuery and add display-friendly derived columns.

    Added columns:
      - winner:  team name that won, derived from the home_win binary flag.
      - score:   score_diff formatted as a signed string (e.g. '+14' or '-8').
      - margin:  absolute value of score_diff, used for closest/biggest-blowout stats.
    """
    df = load_bq_data().copy()
    df["winner"] = df.apply(
        lambda r: r["home_team"] if r["home_win"] == 1 else r["away_team"], axis=1
    )
    df["score"]  = df["score_diff"].apply(lambda x: f"+{x}" if x > 0 else str(x))
    df["margin"] = df["score_diff"].abs()
    return df


df = load_data()

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.metric-card {
    background: #1a1a1a;
    border: 1px solid #00C853;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    height: 100%;
}
.metric-value {
    font-size: 1.55rem;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1.2;
}
.metric-label {
    font-size: 0.72rem;
    color: #888888;
    letter-spacing: 1.5px;
    margin-top: 6px;
    text-transform: uppercase;
}
.section-header {
    color: #00C853;
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
.row-count {
    color: #555555;
    font-size: 0.82rem;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("""
<div style="padding: 28px 0 8px 0;">
    <div style="font-size: 2rem; font-weight: 900; color: #FFFFFF;">🗂 DATA EXPLORER</div>
    <div style="color: #888888; font-size: 0.95rem; margin-top: 6px;">
        218 games. Every possession. Every upset.
    </div>
</div>
<hr style="border: none; border-top: 1px solid #00C853; margin: 12px 0 28px 0;">
""", unsafe_allow_html=True)

# ── Section 1: Quick stats row ────────────────────────────────────────────────

close_row   = df.loc[df["margin"].idxmin()]
blowout_row = df.loc[df["margin"].idxmax()]
avg_margin  = df["margin"].mean()

stats = [
    ("TOTAL GAMES",     str(len(df))),
    ("AVG MARGIN",      f"{avg_margin:.1f} pts"),
    ("CLOSEST GAME",    f"{close_row['away_team']} vs {close_row['home_team']} — {close_row['margin']} pt"),
    ("BIGGEST BLOWOUT", f"{blowout_row['away_team']} vs {blowout_row['home_team']} — {blowout_row['margin']} pts"),
]

for col, (label, value) in zip(st.columns(4), stats):
    with col:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-value'>{value}</div>"
            f"<div class='metric-label'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)

# ── Section 2: Filters ────────────────────────────────────────────────────────

all_teams = sorted(set(df["home_team"].tolist() + df["away_team"].tolist()))

col_team, col_result, col_margin = st.columns(3)

with col_team:
    team_filter = st.selectbox("Filter by Team", ["All Teams"] + all_teams)

with col_result:
    result_filter = st.radio("Show", ["All Games", "Home Wins", "Away Wins"], horizontal=False)

with col_margin:
    margin_filter = st.slider("Max Point Margin", min_value=1, max_value=60, value=60)

# Apply filters
filtered = df.copy()

if team_filter != "All Teams":
    filtered = filtered[
        (filtered["home_team"] == team_filter) | (filtered["away_team"] == team_filter)
    ]

if result_filter == "Home Wins":
    filtered = filtered[filtered["winner"] == filtered["home_team"]]
elif result_filter == "Away Wins":
    filtered = filtered[filtered["winner"] == filtered["away_team"]]

filtered = filtered[filtered["margin"] <= margin_filter]

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# ── Section 3: Games table ────────────────────────────────────────────────────

display_cols = {}
if "date" in filtered.columns:
    display_cols["date"] = "Date"
display_cols.update({
    "home_team": "Home Team",
    "away_team": "Away Team",
    "score": "Score",
    "winner": "Winner",
    "margin": "Margin",
})

table_df = filtered[[c for c in display_cols if c in filtered.columns]].rename(columns=display_cols)

def style_table(styler):
    """Apply dark-theme cell and header styling to the games table."""
    def winner_color(val):
        return "color: #00C853; font-weight: 600;"

    def margin_color(val):
        if val <= 5:
            return "color: #00C853;"
        elif val >= 20:
            return "color: #FF1744;"
        return "color: #FFFFFF;"

    styler.applymap(winner_color, subset=["Winner"])
    styler.applymap(margin_color, subset=["Margin"])
    styler.set_properties(**{
        "background-color": "#1a1a1a",
        "color": "#FFFFFF",
        "border-color": "#2a2a2a",
    })
    styler.set_table_styles([
        {"selector": "th", "props": [
            ("background-color", "#111111"),
            ("color", "#00C853"),
            ("font-size", "0.8rem"),
            ("letter-spacing", "1px"),
            ("text-transform", "uppercase"),
            ("border-bottom", "1px solid #00C853"),
        ]},
        {"selector": "tr:hover td", "props": [("background-color", "#242424")]},
    ])
    return styler

st.dataframe(
    table_df.style.pipe(style_table),
    use_container_width=True,
    hide_index=True,
)

st.markdown(
    f"<div class='row-count'>Showing {len(filtered)} of {len(df)} games</div>",
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)

# ── Section 4: Team records ───────────────────────────────────────────────────

st.markdown("<div class='section-header'>📋 TEAM RECORDS</div>", unsafe_allow_html=True)

wins_series  = df["winner"].value_counts()
games_home   = df["home_team"].value_counts()
games_away   = df["away_team"].value_counts()
total_games  = (games_home.add(games_away, fill_value=0)).astype(int)

records = pd.DataFrame({
    "W": wins_series,
    "Games": total_games,
}).fillna(0).astype(int)

records["L"] = records["Games"] - records["W"]
records["Win%"] = (records["W"] / records["Games"] * 100).round(1)
records = records.drop(columns=["Games"]).sort_values("Win%", ascending=False).reset_index()
records.rename(columns={"index": "Team"}, inplace=True)

medals = {0: "🥇", 1: "🥈", 2: "🥉"}
records["Team"] = records.apply(
    lambda r: f"{medals[r.name]} {r['Team']}" if r.name in medals else r["Team"], axis=1
)

def style_records(styler):
    """Apply dark-theme styling and a win-percentage bar to the team records table."""
    styler.set_properties(**{
        "background-color": "#1a1a1a",
        "color": "#FFFFFF",
        "border-color": "#2a2a2a",
    })
    styler.set_table_styles([
        {"selector": "th", "props": [
            ("background-color", "#111111"),
            ("color", "#00C853"),
            ("font-size", "0.8rem"),
            ("letter-spacing", "1px"),
            ("text-transform", "uppercase"),
            ("border-bottom", "1px solid #00C853"),
        ]},
        {"selector": "tr:hover td", "props": [("background-color", "#242424")]},
    ])
    styler.bar(subset=["Win%"], color="#00C853", vmin=0, vmax=100)
    return styler

st.dataframe(
    records[["Team", "W", "L", "Win%"]].style.pipe(style_records),
    use_container_width=True,
    hide_index=True,
)
