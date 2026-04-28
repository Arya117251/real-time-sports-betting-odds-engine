"""Shared utilities: BigQuery data loading, model loading, and prediction helpers."""

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from google.cloud import bigquery

import config

FEATURES = [
    "season_home_win_pct",
    "season_away_win_pct",
    "home_rest_days",
    "away_rest_days",
    "home_is_back_to_back",
    "away_is_back_to_back",
    "home_wins",
    "away_wins",
    "home_losses",
    "away_losses",
]


def load_model():
    """Load the trained RandomForest model from models/win_predictor.pkl.

    Raises FileNotFoundError with an actionable message if the model has not
    been trained yet.
    """
    path = config.MODEL_PATHS["model"]
    try:
        return joblib.load(path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Model not found at {path}. Run scripts/train_model.py first."
        ) from None


@st.cache_data(ttl=3600)
def load_bq_data() -> pd.DataFrame:
    """Fetch all rows from nba_gold.gold_game_features via Application Default Credentials.

    Results are cached for 1 hour (ttl=3600) to avoid redundant BigQuery queries
    on each Streamlit re-render.  Cache is shared across pages within the same
    Streamlit server process.
    """
    client = bigquery.Client(project="sports-odds-engine")
    df = client.query(f"SELECT * FROM `{config.BQ_TABLE}`").to_dataframe()
    return df


def get_team_latest_features(df: pd.DataFrame, home_team: str, away_team: str) -> dict:
    """Look up the most recent season stats for two teams and return a feature dict.

    Used by the Live Predictions page where only team names are known, not their
    current season numbers.  Searches for the last game each team played as the
    home/away side respectively and pulls that row's feature values.  Falls back
    to column medians when a team has no history in the dataset.
    """
    medians = df[FEATURES].median()

    home_rows = df[df["home_team"] == home_team].sort_values("date")
    away_rows = df[df["away_team"] == away_team].sort_values("date")

    home_stats = home_rows.iloc[-1] if len(home_rows) else medians
    away_stats = away_rows.iloc[-1] if len(away_rows) else medians

    def _get(series, col):
        val = series.get(col) if hasattr(series, "get") else series[col]
        return float(val) if pd.notna(val) else float(medians[col])

    return {
        "season_home_win_pct":  _get(home_stats, "season_home_win_pct"),
        "season_away_win_pct":  _get(away_stats, "season_away_win_pct"),
        "home_rest_days":       _get(home_stats, "home_rest_days"),
        "away_rest_days":       _get(away_stats, "away_rest_days"),
        "home_is_back_to_back": 0,
        "away_is_back_to_back": 0,
        "home_wins":            _get(home_stats, "home_wins"),
        "away_wins":            _get(away_stats, "away_wins"),
        "home_losses":          _get(home_stats, "home_losses"),
        "away_losses":          _get(away_stats, "away_losses"),
    }


def prob_to_american_odds(prob: float) -> int:
    """Convert a win probability in [0, 1] to American moneyline odds."""
    if prob >= 0.5:
        return round(-100 * prob / (1 - prob))
    return round(100 * (1 - prob) / prob)


def predict_winner(home_team: str, away_team: str, feature_row, model) -> dict:
    """Run the model against one game's numeric features and return a prediction dict.

    Args:
        home_team:   Display name of the home team.
        away_team:   Display name of the away team.
        feature_row: Dict or Series containing the 10 numeric feature columns
                     the model was trained on (see FEATURES list above).
        model:       Trained sklearn estimator with a predict_proba method.

    Returns a dict with home_win_prob, away_win_prob, American moneyline odds
    for each side, and predicted_winner.
    """
    X = np.array([[feature_row[f] for f in FEATURES]])
    proba = model.predict_proba(X)[0]
    home_win_prob = float(proba[1])
    away_win_prob = float(proba[0])

    return {
        "home_team":        home_team,
        "away_team":        away_team,
        "home_win_prob":    home_win_prob,
        "away_win_prob":    away_win_prob,
        "home_odds":        prob_to_american_odds(home_win_prob),
        "away_odds":        prob_to_american_odds(away_win_prob),
        "predicted_winner": home_team if home_win_prob >= away_win_prob else away_team,
    }
