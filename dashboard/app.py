from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import threading
import time

app = Flask(__name__)

latest_patients = {}


def kafka_listener():
    while True:
        try:
            print("Connecting to Kafka...")

            consumer = KafkaConsumer(
                "patient-vitals-processed",
                bootstrap_servers=["kafka:9092"],
                auto_offset_reset="latest",
                enable_auto_commit=True,
                consumer_timeout_ms=1000,
                api_version_auto_timeout_ms=10000,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            print("✅ Dashboard connected to Kafka!")

            while True:
                for message in consumer:
                    data = message.value
                    latest_patients[data["patient_id"]] = data

        except NoBrokersAvailable:
            print("❌ Kafka not ready. Retrying in 5 seconds...")
            time.sleep(5)

        except Exception as e:
            print("Dashboard Error:", e)
            time.sleep(5)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/patients")
def patients():
    return jsonify(list(latest_patients.values()))


if __name__ == "__main__":
    threading.Thread(target=kafka_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)