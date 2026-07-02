from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import threading
import time
from datetime import datetime

app = Flask(__name__)

latest_patients = {}
last_updated = ""


def kafka_listener():
    global last_updated

    while True:
        try:
            print("Connecting to Kafka...")

            consumer = KafkaConsumer(
                "patient-vitals-processed",
                bootstrap_servers=["kafka:9092"],
                auto_offset_reset="latest",
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            print("Dashboard Connected to Kafka!")

            for message in consumer:

                data = message.value

                latest_patients[data["patient_id"]] = data

                last_updated = datetime.now().strftime("%H:%M:%S")

        except NoBrokersAvailable:

            print("Kafka not ready...")
            time.sleep(5)

        except Exception as e:

            print(e)
            time.sleep(5)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/patients")
def patients():

    patients = list(latest_patients.values())

    total = len(patients)

    critical = sum(
        1 for p in patients
        if p["status"] == "CRITICAL"
    )

    normal = total - critical

    return jsonify({

        "patients": patients,

        "summary": {

            "total": total,
            "critical": critical,
            "normal": normal,
            "updated": last_updated

        }

    })


if __name__ == "__main__":

    threading.Thread(
        target=kafka_listener,
        daemon=True
    ).start()

    app.run(host="0.0.0.0", port=5000)