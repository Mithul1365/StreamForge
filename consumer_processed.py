import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'patient-vitals-processed',
    bootstrap_servers=['localhost:29092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("📊 Processed Data Consumer starting...")
print("Flink se processed data padh raha hoon...\n")

for message in consumer:
    data = message.value
    print(f"✅ Processed: {data}")