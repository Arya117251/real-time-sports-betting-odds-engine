from google.cloud import pubsub_v1
import json

project_id = "sports-odds-engine"
subscription_id = "live-nba-games-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    data = json.loads(message.data.decode('utf-8'))
    
    for game in data.get('events', [])[:5]:  # Show first 5 games
        comp = game['competitions'][0]
        home = comp['competitors'][0]
        away = comp['competitors'][1]
        status = game['status']['type']['detail']
        
        print(f"\n{away['team']['displayName']:25} {away.get('score', 0):>3}")
        print(f"{home['team']['displayName']:25} {home.get('score', 0):>3}")
        print(f"Status: {status}")
    
    message.ack()
    print("\n" + "="*50)
    return

print("📊 Showing game scores from captured data...\n")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    streaming_pull_future.result(timeout=10)
except:
    streaming_pull_future.cancel()
