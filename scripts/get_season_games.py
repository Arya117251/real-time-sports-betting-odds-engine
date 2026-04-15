import requests
import csv
from datetime import datetime, timedelta

csv_file = 'nba_games.csv'

# Get games from last 30 days
start_date = datetime.now() - timedelta(days=30)

print("📥 Fetching season games...")

with open(csv_file, 'a', newline='') as f:
    writer = csv.writer(f)
    
    for i in range(30):
        date = (start_date + timedelta(days=i)).strftime('%Y%m%d')
        url = f'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date}'
        
        try:
            response = requests.get(url)
            data = response.json()
            
            for game in data.get('events', []):
                if game['status']['type']['completed']:  # Only finished games
                    comp = game['competitions'][0]
                    home = comp['competitors'][0]
                    away = comp['competitors'][1]
                    
                    writer.writerow([
                        date,
                        game['id'],
                        home['team']['displayName'],
                        away['team']['displayName'],
                        int(home.get('score', 0)),
                        int(away.get('score', 0)),
                        'Final'
                    ])
            
            print(f"✅ Got {len(data.get('events', []))} games from {date}")
            
        except:
            print(f"❌ No data for {date}")

print("\n🎉 Done! Re-run clean_data.py now")
