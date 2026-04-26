import joblib
import numpy as np
import config


def load_models():
    try:
        return {
            "model": joblib.load(config.MODEL_PATHS["model"]),
            "home_encoder": joblib.load(config.MODEL_PATHS["home_encoder"]),
            "away_encoder": joblib.load(config.MODEL_PATHS["away_encoder"]),
        }
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Model file not found: {e.filename}. Ensure all model files exist in models/") from e


def prob_to_american_odds(prob):
    if prob >= 0.5:
        return round(-100 * prob / (1 - prob))
    return round(100 * (1 - prob) / prob)


def predict_winner(home_team, away_team, models):
    home_encoded = models["home_encoder"].transform([home_team])[0]
    away_encoded = models["away_encoder"].transform([away_team])[0]

    features = np.array([[home_encoded, away_encoded]])
    proba = models["model"].predict_proba(features)[0]

    home_win_prob = float(proba[1])
    away_win_prob = float(proba[0])

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_win_prob": home_win_prob,
        "away_win_prob": away_win_prob,
        "home_odds": prob_to_american_odds(home_win_prob),
        "away_odds": prob_to_american_odds(away_win_prob),
        "predicted_winner": home_team if home_win_prob >= away_win_prob else away_team,
    }
