import pandas as pd

# Load CSV
df = pd.read_csv('data/nba_games.csv')

print(f"Total rows: {len(df)}")

# Remove duplicates - simpler approach
df = df.drop_duplicates()

# Keep only finished games
df = df[df['status'] == 'Final']

# Add winner column
df['home_wins'] = (df['home_score'] > df['away_score']).astype(int)

# Add score difference
df['score_diff'] = df['home_score'] - df['away_score']

# Save
df.to_csv('data/clean_games.csv', index=False)

print(f"Clean rows: {len(df)}")
print(df.head())
