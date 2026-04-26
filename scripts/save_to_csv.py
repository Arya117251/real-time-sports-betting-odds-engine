from google.cloud import pubsub_v1
import json
import csv
from datetime import datetime

project_id = "sports-odds-engine"
subscription_id = "live-nba-games-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

csv_file = open('nba_games.csv', 'a', newline='')
writer = csv.writer(csv_file)

if csv_file.tell() == 0:
    writer.writerow(['timestamp', 'game_id', 'home_team', 'away_team', 'home_score', 'away_score', 'status'])

def callback(message):
    data = json.loads(message.data.decode('utf-8'))
    
    for game in data.get('events', []):
        comp = game['competitions'][0]
        home = comp['competitors'][0]
        away = comp['competitors'][1]
        
        writer.writerow([
            datetime.utcnow().isoformat(),
            game['id'],
            home['team']['displayName'],
            away['team']['displayName'],
            int(home.get('score', 0)),
            int(away.get('score', 0)),
            game['status']['type']['detail']
        ])
    
    csv_file.flush()
    print(f"✅ Saved {len(data.get('events', []))} games")
    message.ack()

print("💾 Saving to CSV...")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    csv_file.close()
    streaming_pull_future.cancel()
