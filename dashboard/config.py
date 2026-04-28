from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COLORS = {
    "green": "#00C853",
    "red": "#FF1744",
    "background": "#121212",
    "card": "#1E1E1E",
    "text": "#FFFFFF"
}

UPCOMING_GAMES = [
    {"label": "Lakers @ Celtics - Tonight 7:00 PM", "home_team": "Boston Celtics", "away_team": "Los Angeles Lakers", "time": "7:00 PM ET"},
    {"label": "Warriors @ Heat - Tonight 9:30 PM", "home_team": "Miami Heat", "away_team": "Golden State Warriors", "time": "9:30 PM ET"},
    {"label": "Nuggets @ Bucks - Tomorrow 8:00 PM", "home_team": "Milwaukee Bucks", "away_team": "Denver Nuggets", "time": "8:00 PM ET"},
]

TEAM_NAMES = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
    "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons",
    "Golden State Warriors", "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers",
    "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat", "Milwaukee Bucks",
    "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder",
    "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
    "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"
]

MODEL_PATHS = {
    "model": ROOT / "models" / "win_predictor.pkl",
}

BQ_TABLE = "sports-odds-engine.nba_gold.gold_game_features"
