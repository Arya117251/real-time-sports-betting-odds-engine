import streamlit as st
from utils import load_models, predict_winner
from config import UPCOMING_GAMES, COLORS

# ── Session state ─────────────────────────────────────────────────────────────

if "models" not in st.session_state:
    st.session_state["models"] = load_models()

if "bet_slip" not in st.session_state:
    st.session_state["bet_slip"] = []

models = st.session_state["models"]

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.game-card {
    background: #1a1a1a;
    border-left: 3px solid #00C853;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: box-shadow 0.2s ease;
}
.game-card:hover {
    box-shadow: 0 0 18px #00C85344;
}
.team-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #FFFFFF;
}
.odds-fav {
    font-size: 1.6rem;
    font-weight: 700;
    color: #00C853;
}
.odds-dog {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FF1744;
}
.win-prob {
    font-size: 0.8rem;
    color: #888888;
    margin-top: 2px;
}
.payout-value {
    color: #00C853;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("""
<div style="padding: 28px 0 8px 0;">
    <div style="font-size: 2rem; font-weight: 900; color: #FFFFFF;">🏀 TONIGHT'S GAMES</div>
    <div style="color: #888888; font-size: 0.95rem; margin-top: 6px;">
        Live AI Predictions | Odds update with every pick
    </div>
</div>
<hr style="border: none; border-top: 1px solid #00C853; margin: 12px 0 24px 0;">
""", unsafe_allow_html=True)

# ── Featured matchups ─────────────────────────────────────────────────────────

st.markdown(
    "<div style='text-align:center; color:#555555; font-size:0.8rem; letter-spacing:2px; margin-bottom:20px;'>"
    "— FEATURED MATCHUPS —</div>",
    unsafe_allow_html=True,
)

for game in UPCOMING_GAMES:
    result = predict_winner(game["home_team"], game["away_team"], models)

    home_prob = result["home_win_prob"]
    away_prob = result["away_win_prob"]
    home_odds = result["home_odds"]
    away_odds = result["away_odds"]

    home_is_fav = home_prob >= away_prob

    home_odds_class = "odds-fav" if home_is_fav else "odds-dog"
    away_odds_class = "odds-fav" if not home_is_fav else "odds-dog"

    def fmt_odds(o):
        return f"+{o}" if o > 0 else str(o)

    st.markdown(f"""
    <div class="game-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span class="team-name">{game['away_team']}</span>
            <span style="color:#555555; font-size:0.8rem;">{game['time']}</span>
            <span class="team-name">{game['home_team']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_away, col_home = st.columns([1, 1])

    with col_away:
        st.markdown(
            f"<div class='{away_odds_class}'>{fmt_odds(away_odds)}</div>"
            f"<div class='win-prob'>{round(away_prob * 100)}% win</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            f"BET {game['away_team']}",
            key=f"bet_away_{game['label']}",
            type="primary" if not home_is_fav else "secondary",
        ):
            st.session_state["bet_slip"].append({
                "team": game["away_team"],
                "odds": away_odds,
                "label": game["label"],
                "wager": 10.0,
            })
            st.rerun()

    with col_home:
        st.markdown(
            f"<div class='{home_odds_class}'>{fmt_odds(home_odds)}</div>"
            f"<div class='win-prob'>{round(home_prob * 100)}% win</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            f"BET {game['home_team']}",
            key=f"bet_home_{game['label']}",
            type="primary" if home_is_fav else "secondary",
        ):
            st.session_state["bet_slip"].append({
                "team": game["home_team"],
                "odds": home_odds,
                "label": game["label"],
                "wager": 10.0,
            })
            st.rerun()

    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ── Bet slip sidebar ──────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<div style='font-weight:700; color:#00C853; font-size:1.1rem; margin-bottom:8px;'>📋 BET SLIP</div>",
        unsafe_allow_html=True,
    )

    bet_slip = st.session_state["bet_slip"]

    if not bet_slip:
        st.markdown(
            "<div style='color:#555555; font-style:italic; font-size:0.9rem;'>No bets added yet</div>",
            unsafe_allow_html=True,
        )
    else:
        total_payout = 0.0
        to_remove = []

        for i, bet in enumerate(bet_slip):
            odds = bet["odds"]
            st.markdown(
                f"<div style='font-weight:600; color:#FFFFFF; font-size:0.95rem;'>{bet['team']}</div>"
                f"<div style='color:#888888; font-size:0.75rem; margin-bottom:4px;'>{bet['label']}</div>",
                unsafe_allow_html=True,
            )

            wager = st.number_input(
                "Wager ($)",
                min_value=1.0,
                max_value=1000.0,
                value=float(bet.get("wager", 10.0)),
                step=1.0,
                key=f"wager_{i}",
                label_visibility="collapsed",
            )
            bet_slip[i]["wager"] = wager

            if odds < 0:
                payout = wager + (wager * 100 / abs(odds))
            else:
                payout = wager + (wager * odds / 100)

            total_payout += payout

            col_payout, col_remove = st.columns([2, 1])
            with col_payout:
                st.markdown(
                    f"<div class='payout-value'>→ ${payout:.2f}</div>",
                    unsafe_allow_html=True,
                )
            with col_remove:
                if st.button("✕", key=f"remove_{i}"):
                    to_remove.append(i)

            st.markdown("<hr style='border-color:#222222; margin:8px 0;'>", unsafe_allow_html=True)

        for idx in sorted(to_remove, reverse=True):
            bet_slip.pop(idx)
        if to_remove:
            st.rerun()

        st.markdown(
            f"<div style='font-size:1.1rem; font-weight:700; color:#00C853; margin:8px 0;'>"
            f"Total payout: ${total_payout:.2f}</div>",
            unsafe_allow_html=True,
        )

        if st.button("PLACE BET 🎰", type="primary", use_container_width=True):
            st.success("Bet placed! Good luck... you'll need it.")

        if st.button("Clear All", use_container_width=True):
            st.session_state["bet_slip"] = []
            st.rerun()
