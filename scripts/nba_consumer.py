from google.cloud import pubsub_v1
import json

project_id = "sports-odds-engine"
subscription_id = "live-nba-games-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    data = json.loads(message.data.decode('utf-8'))
    print(f"\n🏀 Received NBA data:")
    print(f"League: {data.get('leagues', [{}])[0].get('name', 'NBA')}")
    print(f"Events: {len(data.get('events', []))} games")
    message.ack()

print("👂 Listening for NBA data...")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
