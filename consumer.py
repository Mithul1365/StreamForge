import json
from kafka import KafkaConsumer

# Connect to Kafka
consumer = KafkaConsumer(
    'patient-vitals',
    bootstrap_servers=['localhost:29092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Patient Monitor Consumer starting...")
print("Reading data from Kafka...\n")

for message in consumer:
    data = message.value

    # Check normal vs anomaly
    if data['heart_rate'] > 120 or data['spo2'] < 90:
        print(f"ALERT! Patient {data['patient_id']} - HR: {data['heart_rate']}, SpO2: {data['spo2']}%")
    else:
        print(f"Normal - Patient {data['patient_id']} - HR: {data['heart_rate']}, SpO2: {data['spo2']}%")