import requests
import csv
from datetime import datetime, timedelta
from collections import defaultdict

OUTPUT_FILE = 'data/nba_games_raw.csv'
DAYS_BACK = 60

print("Fetching NBA games with engineered features...")

start_date = datetime.now() - timedelta(days=DAYS_BACK)
last_game_date = defaultdict(lambda: None)

fieldnames = [
    'game_id', 'date', 'home_team', 'away_team',
    'home_score', 'away_score', 'status',
    'home_wins', 'away_wins', 'home_losses', 'away_losses',
    'season_home_win_pct', 'season_away_win_pct',
    'home_rest_days', 'away_rest_days',
    'home_is_back_to_back', 'away_is_back_to_back',
    'score_diff'
]

with open(OUTPUT_FILE, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(DAYS_BACK):
        date_obj = start_date + timedelta(days=i)
        date_str = date_obj.strftime('%Y%m%d')
        date_clean = date_obj.strftime('%Y-%m-%d')

        url = f'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}'

        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            games = data.get('events', [])
            count = 0

            for game in games:
                if not game['status']['type']['completed']:
                    continue

                comp = game['competitions'][0]
                competitors = comp['competitors']

                home = next((t for t in competitors if t['homeAway'] == 'home'), competitors[0])
                away = next((t for t in competitors if t['homeAway'] == 'away'), competitors[1])

                home_name = home['team']['displayName']
                away_name = away['team']['displayName']
                home_score = int(home.get('score', 0))
                away_score = int(away.get('score', 0))

                def parse_record(team):
                    try:
                        summary = team.get('records', [{}])[0].get('summary', '0-0')
                        w, l = summary.split('-')
                        return int(w), int(l)
                    except:
                        return 0, 0

                home_wins, home_losses = parse_record(home)
                away_wins, away_losses = parse_record(away)

                season_home_win_pct = round(home_wins / (home_wins + home_losses), 3) if (home_wins + home_losses) > 0 else 0.0
                season_away_win_pct = round(away_wins / (away_wins + away_losses), 3) if (away_wins + away_losses) > 0 else 0.0

                def get_rest(team_name, current_date):
                    last = last_game_date[team_name]
                    if last is None:
                        return 7, 0
                    delta = (current_date - last).days
                    return delta, 1 if delta == 1 else 0

                home_rest, home_b2b = get_rest(home_name, date_obj)
                away_rest, away_b2b = get_rest(away_name, date_obj)

                last_game_date[home_name] = date_obj
                last_game_date[away_name] = date_obj

                writer.writerow({
                    'game_id': game['id'],
                    'date': date_clean,
                    'home_team': home_name,
                    'away_team': away_name,
                    'home_score': home_score,
                    'away_score': away_score,
                    'status': 'Final',
                    'home_wins': home_wins,
                    'away_wins': away_wins,
                    'home_losses': home_losses,
                    'away_losses': away_losses,
                    'season_home_win_pct': season_home_win_pct,
                    'season_away_win_pct': season_away_win_pct,
                    'home_rest_days': home_rest,
                    'away_rest_days': away_rest,
                    'home_is_back_to_back': home_b2b,
                    'away_is_back_to_back': away_b2b,
                    'score_diff': home_score - away_score
                })
                count += 1

            print(f"{date_clean} — {count} finished games")

        except Exception as e:
            print(f"Failed {date_clean}: {e}")

print(f"\nDone. Saved to {OUTPUT_FILE}")