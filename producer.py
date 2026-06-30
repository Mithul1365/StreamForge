import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# Wait until Kafka is ready
while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        print("Connected to Kafka!")
        break
    except Exception:
        print("Waiting for Kafka...")
        time.sleep(5)

patients = ['P001', 'P002', 'P003']

def generate_patient_data(patient_id):
    data = {
        "patient_id": patient_id,
        "heart_rate": random.randint(60, 100),
        "spo2": random.randint(95, 100),
        "bp_systolic": random.randint(110, 130),
        "temperature": round(random.uniform(97.0, 99.0), 1),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 10% anomaly
    if random.random() < 0.1:
        data["heart_rate"] = random.randint(130, 160)
        data["spo2"] = random.randint(80, 88)
        print(f"ANOMALY generated for {patient_id}")

    return data

print("Producer Started...")

while True:
    for patient in patients:
        data = generate_patient_data(patient)
        producer.send("patient-vitals", value=data)
        producer.flush()
        print("Sent:", data)

    time.sleep(2)