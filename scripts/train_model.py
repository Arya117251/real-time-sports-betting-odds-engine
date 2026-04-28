"""Train a RandomForest win-prediction model from the gold BigQuery feature table."""

import pathlib
import joblib
import pandas as pd
from google.cloud import bigquery
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

PROJECT_ID = "sports-odds-engine"
TABLE     = f"{PROJECT_ID}.nba_gold.gold_game_features"
MODELS_DIR = pathlib.Path(__file__).parent.parent / "models"

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
TARGET = "home_win"


def load_data() -> pd.DataFrame:
    """Query gold_game_features from BigQuery using Application Default Credentials.

    Returns a DataFrame containing only the feature columns and the target column
    so downstream steps never accidentally touch raw score data.
    """
    client = bigquery.Client(project=PROJECT_ID)
    cols = ", ".join(FEATURES + [TARGET])
    query = f"SELECT {cols} FROM `{TABLE}`"
    df = client.query(query).to_dataframe()
    print(f"Loaded {len(df)} rows from {TABLE}")
    return df


def split(df: pd.DataFrame):
    """Split DataFrame into train/test sets with an 80/20 ratio.

    Returns (X_train, X_test, y_train, y_test) using a fixed random seed so
    results are reproducible across runs.
    """
    X = df[FEATURES]
    y = df[TARGET]
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Fit a RandomForestClassifier on the training split and return it."""
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model


def evaluate(model: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> float:
    """Compute and print accuracy on the held-out test split.

    Returns the accuracy as a float in [0, 1].
    """
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Accuracy: {acc * 100:.1f}%")
    return acc


def save_model(model: RandomForestClassifier) -> None:
    """Persist the trained model to models/win_predictor.pkl.

    Creates the models/ directory if it does not already exist.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    path = MODELS_DIR / "win_predictor.pkl"
    joblib.dump(model, path)
    print(f"Model saved to {path}")


def main() -> None:
    """Orchestrate data loading, training, evaluation, and model persistence."""
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)
    print("Training...")
    model = train(X_train, y_train)
    evaluate(model, X_test, y_test)
    save_model(model)


if __name__ == "__main__":
    main()
