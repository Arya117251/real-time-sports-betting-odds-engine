import requests
import json
import time
from google.cloud import pubsub_v1

# Setup
project_id = "sports-odds-engine"
topic_id = "live-nba-games"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

print("🏀 NBA Data Producer Started...")

while True:
    try:
        # Fetch live NBA scores
        response = requests.get(
            'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'
        )
        data = response.json()
        
        # Publish to Pub/Sub
        message = json.dumps(data).encode('utf-8')
        future = publisher.publish(topic_path, message)
        
        print(f"✅ Published NBA data at {time.strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(30)  # Fetch every 30 seconds
