import json
import time
from kafka import KafkaConsumer

# Wait until Kafka is ready
while True:
    try:
        consumer = KafkaConsumer(
            "patient-vitals",
            bootstrap_servers="kafka:9092",
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )
        print("Connected to Kafka!")
        break
    except Exception:
        print("Waiting for Kafka...")
        time.sleep(5)

print("Consumer Started...")

for message in consumer:
    data = message.value

    if data["heart_rate"] > 120 or data["spo2"] < 90:
        print(
            f"ALERT -> {data['patient_id']} | HR={data['heart_rate']} | SpO2={data['spo2']}"
        )
    else:
        print(
            f"NORMAL -> {data['patient_id']} | HR={data['heart_rate']} | SpO2={data['spo2']}"
        )