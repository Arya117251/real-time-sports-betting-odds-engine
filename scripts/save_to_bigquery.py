from google.cloud import pubsub_v1, bigquery
import json
from datetime import datetime

project_id = "sports-odds-engine"
subscription_id = "live-nba-games-sub"
dataset_id = "nba_data"
table_id = "game_results"

subscriber = pubsub_v1.SubscriberClient()
bq_client = bigquery.Client()

subscription_path = subscriber.subscription_path(project_id, subscription_id)
table_ref = f"{project_id}.{dataset_id}.{table_id}"

def callback(message):
    data = json.loads(message.data.decode('utf-8'))
    
    rows_to_insert = []
    for game in data.get('events', []):
        comp = game['competitions'][0]
        home = comp['competitors'][0]
        away = comp['competitors'][1]
        
        row = {
            "game_id": game['id'],
            "home_team": home['team']['displayName'],
            "away_team": away['team']['displayName'],
            "home_score": int(home.get('score', 0)),
            "away_score": int(away.get('score', 0)),
            "status": game['status']['type']['detail'],
            "timestamp": datetime.utcnow().isoformat()
        }
        rows_to_insert.append(row)
    
    errors = bq_client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print(f"❌ Errors: {errors}")
    else:
        print(f"✅ Saved {len(rows_to_insert)} games to BigQuery")
    
    message.ack()

print("💾 Saving NBA data to BigQuery...")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
