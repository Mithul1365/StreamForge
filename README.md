# StreamForge

**A cloud-native, real-time ICU patient monitoring platform** that ingests live patient vitals via Apache Kafka, processes streams using Apache Flink, detects anomalies using an LSTM Autoencoder (PyTorch), and exposes results via a FastAPI service.

---

## Why this project is different

Most student data projects are batch ETL pipelines that load a CSV into Postgres. StreamForge is a real-time streaming system:

- Ingests continuous patient vital sign data using **Kafka**
- Processes and validates data in real-time with **Apache Flink**
- Detects abnormal patient conditions using an **LSTM Autoencoder** (unsupervised anomaly detection)
- Exposes live alerts through a **FastAPI** REST endpoint
- Designed to run 24/7 with containerized infrastructure (**Docker**)

---

## Architecture

Patient Sensor Data

|

v

[ Kafka Topic: patient-vitals ]

|

v

[ Apache Flink Job ]

Validates incoming data
Cleans and enriches records
Tags status as NORMAL / CRITICAL

|

v

[ Kafka Topic: patient-vitals-processed ]

|

v

[ LSTM Autoencoder Model ]
Learns normal patient vital patterns
Flags anomalies via reconstruction error

|

v

[ Kafka Topic: alerts ]

|

v

[ FastAPI Service ]
/health  -> system health check
/alerts  -> live critical alerts



---

## Tech Stack

| Component          | Technology                 |
|---------------------|------------------------------|
| Message Streaming   | Apache Kafka                |
| Stream Processing   | Apache Flink (PyFlink)      |
| Anomaly Detection    | LSTM Autoencoder (PyTorch)  |
| API Layer            | FastAPI                     |
| Containerization     | Docker / Docker Compose     |

---

## How It Works

1. **Producer** (`producer.py`) simulates real-time ICU patient vitals (heart rate, SpO2, blood pressure, temperature) and publishes them to Kafka.
2. **Flink job** (`flink_jobs/patient_processor.py`) consumes the raw vitals, validates and cleans them, tags each record's status, and republishes to a processed topic.
3. **LSTM Autoencoder** (`lstm_model.py`) is trained on normal patient vitals, learning what a "normal" pattern looks like. It continuously consumes the processed stream and calculates a reconstruction error for every reading — a high error means the pattern doesn't match anything normal, indicating a possible medical emergency.
4. Detected anomalies are published to an `alerts` Kafka topic.
5. **FastAPI** (`api.py`) exposes a `/alerts` endpoint that surfaces the most recent critical alerts in real time.

---

## Setup & Running Locally

### Prerequisites
- Docker Desktop
- Python 3.10+

### 1. Start infrastructure
```bash
docker-compose up -d
```

### 2. Submit the Flink job
```bash
docker cp flink_jobs/patient_processor.py streamforge-flink-jobmanager-1:/opt/flink/
docker exec streamforge-flink-jobmanager-1 flink run -py /opt/flink/patient_processor.py
```

### 3. Install Python dependencies
```bash
pip install kafka-python torch numpy fastapi uvicorn
```

### 4. Run the pipeline (separate terminals)
```bash
python producer.py
python lstm_model.py
uvicorn api:app --reload
```

### 5. Check live alerts
Visit: `http://127.0.0.1:8000/alerts`

---

## Project Status

- [x] Kafka producer & consumer
- [x] Apache Flink stream processing job
- [x] LSTM Autoencoder anomaly detection
- [x] FastAPI alert endpoint
- [ ] Apache Iceberg / S3 storage layer
- [ ] Kubernetes deployment
- [ ] Grafana monitoring dashboard

---

## Author

Built as part of a two-developer collaborative project covering real-time data engineering and platform engineering.