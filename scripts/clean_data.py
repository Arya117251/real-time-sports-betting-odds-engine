import pandas as pd

df = pd.read_csv('data/nba_games.csv')

print(f"Total rows: {len(df)}")

df = df.drop_duplicates()

df = df[df['status'] == 'Final']

df['home_wins'] = (df['home_score'] > df['away_score']).astype(int)

df['score_diff'] = df['home_score'] - df['away_score']

df.to_csv('data/clean_games.csv', index=False)

print(f"Clean rows: {len(df)}")
print(df.head())
