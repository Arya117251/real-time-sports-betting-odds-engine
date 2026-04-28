import pandas as pd

df = pd.read_csv('data/nba_games_raw.csv')
print(f"Raw rows: {len(df)}")

# Deduplicate on game_id
df = df.drop_duplicates(subset=['game_id'])

# Only finished games (should already be clean but safety check)
df = df[df['status'] == 'Final']

# Ensure home_wins exists (1 if home won, 0 if not)
df['home_wins'] = (df['score_diff'] > 0).astype(int)

# Drop any rows with nulls in critical columns
df = df.dropna(subset=[
    'home_team', 'away_team', 'home_score', 'away_score',
    'season_home_win_pct', 'season_away_win_pct',
    'home_rest_days', 'away_rest_days',
    'home_is_back_to_back', 'away_is_back_to_back'
])

df.to_csv('data/clean_games.csv', index=False)

print(f"Clean rows: {len(df)}")
print(df.head())