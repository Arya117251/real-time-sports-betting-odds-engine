import pandas as pd

# Load CSV
df = pd.read_csv('nba_games.csv')

print(f"Total rows: {len(df)}")

# Remove duplicates
df = df.drop_duplicates(subset=['game_id', 'home_score', 'away_score'])

# Keep only finished games for training
df = df[df['status'] == 'Final']

# Add winner column (1 = home wins, 0 = away wins)
df['home_wins'] = (df['home_score'] > df['away_score']).astype(int)

# Add score difference
df['score_diff'] = df['home_score'] - df['away_score']

# Save clean data
df.to_csv('clean_games.csv', index=False)

print(f"Clean rows: {len(df)}")
print(df.head())
