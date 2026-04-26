COLORS = {
    "green": "#00C853",
    "red": "#FF1744",
    "background": "#121212",
    "card": "#1E1E1E",
    "text": "#FFFFFF"
}

UPCOMING_GAMES = [
    {"label": "Lakers @ Celtics - Tonight 7:00 PM", "home_team": "Celtics", "away_team": "Lakers", "time": "7:00 PM ET"},
    {"label": "Warriors @ Heat - Tonight 9:30 PM", "home_team": "Heat", "away_team": "Warriors", "time": "9:30 PM ET"},
    {"label": "Nuggets @ Bucks - Tomorrow 8:00 PM", "home_team": "Bucks", "away_team": "Nuggets", "time": "8:00 PM ET"},
]

TEAM_NAMES = [
    "Hawks", "Celtics", "Nets", "Hornets", "Bulls", "Cavaliers", "Mavericks",
    "Nuggets", "Pistons", "Warriors", "Rockets", "Pacers", "Clippers", "Lakers",
    "Grizzlies", "Heat", "Bucks", "Timberwolves", "Pelicans", "Knicks",
    "Thunder", "Magic", "76ers", "Suns", "Trail Blazers", "Kings", "Spurs",
    "Raptors", "Jazz", "Wizards"
]

MODEL_PATHS = {
    "model": "models/win_predictor.pkl",
    "home_encoder": "models/home_encoder.pkl",
    "away_encoder": "models/away_encoder.pkl"
}

DATA_PATH = "data/clean_games.csv"
