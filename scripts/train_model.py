import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

# Load data
df = pd.read_csv('clean_games.csv')

# Encode team names
le_home = LabelEncoder()
le_away = LabelEncoder()

df['home_encoded'] = le_home.fit_transform(df['home_team'])
df['away_encoded'] = le_away.fit_transform(df['away_team'])

# Features: teams only (no scores)
X = df[['home_encoded', 'away_encoded']]
y = df['home_wins']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training models...\n")

# Random Forest
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)
rf_acc = accuracy_score(y_test, rf.predict(X_test))

print(f"Random Forest: {rf_acc*100:.1f}%")

# Save
joblib.dump(rf, 'win_predictor.pkl')
joblib.dump(le_home, 'home_encoder.pkl')
joblib.dump(le_away, 'away_encoder.pkl')

print(f"\n✅ Saved model")
