from fastapi import FastAPI
from kafka import KafkaConsumer
import json
import threading

app = FastAPI()

# Store recent alerts in memory
recent_alerts = []

def consume_alerts():
    consumer = KafkaConsumer(
        'alerts',
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    for message in consumer:
        alert = message.value
        recent_alerts.append(alert)
        # Keep only last 20 alerts
        if len(recent_alerts) > 20:
            recent_alerts.pop(0)

# Start the Kafka listener in the background
threading.Thread(target=consume_alerts, daemon=True).start()

@app.get("/health")
def health_check():
    return {"status": "running", "service": "StreamForge API"}

@app.get("/alerts")
def get_alerts():
    return {"total_alerts": len(recent_alerts), "alerts": recent_alerts}