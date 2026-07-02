from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

import boto3
import pandas as pd
import pyarrow.parquet as pq

import json
import threading
import time
import tempfile
import os

from datetime import datetime

app = Flask(__name__)

# ----------------------------------------------------
# Live Dashboard Data
# ----------------------------------------------------

latest_patients = {}
last_updated = ""

# ----------------------------------------------------
# MinIO Configuration
# ----------------------------------------------------

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

BUCKET_NAME = "streamforge-data"

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)

# ----------------------------------------------------
# Kafka Listener
# ----------------------------------------------------

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

                value_deserializer=lambda m:
                json.loads(m.decode("utf-8"))

            )

            print("Dashboard Connected to Kafka")

            for message in consumer:

                data = message.value

                latest_patients[
                    data["patient_id"]
                ] = data

                last_updated = datetime.now().strftime(
                    "%H:%M:%S"
                )

        except NoBrokersAvailable:

            print("Kafka not ready...")

            time.sleep(5)

        except Exception as e:

            print("Dashboard Error :", e)

            time.sleep(5)
# ----------------------------------------------------
# Read Patient History from MinIO
# ----------------------------------------------------

def read_patient_history(patient_id):

    history = []

    try:

        objects = s3.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix="patient_data/"
        )

        if "Contents" not in objects:
            return history

        for obj in objects["Contents"]:

            key = obj["Key"]

            if not key.endswith(".parquet"):
                continue

            with tempfile.NamedTemporaryFile(delete=False) as tmp:

                s3.download_fileobj(
                    BUCKET_NAME,
                    key,
                    tmp
                )

                tmp_path = tmp.name

            df = pd.read_parquet(tmp_path)

            os.remove(tmp_path)

            records = df.to_dict("records")

            for row in records:

                if row["patient_id"] == patient_id:

                    history.append(row)

        history.sort(
            key=lambda x: x["timestamp"]
        )

        return history

    except Exception as e:

        print("History Error :", e)

        return []


# ----------------------------------------------------
# Home
# ----------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# ----------------------------------------------------
# Live Patients
# ----------------------------------------------------

@app.route("/patients")
def patients():

    patients = list(
        latest_patients.values()
    )

    total = len(patients)

    critical = sum(

        1

        for p in patients

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


# ----------------------------------------------------
# Patient History API
# ----------------------------------------------------

@app.route("/history/<patient_id>")
def history(patient_id):

    return jsonify(
        read_patient_history(patient_id)
    )            
# ----------------------------------------------------
# Main
# ----------------------------------------------------

if __name__ == "__main__":

    threading.Thread(
        target=kafka_listener,
        daemon=True
    ).start()

    print("=" * 50)
    print(" StreamForge Dashboard Started ")
    print("=" * 50)
    print("Live Dashboard : http://localhost:5000")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

