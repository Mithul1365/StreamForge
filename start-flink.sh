#!/bin/bash

echo "=================================="
echo "Starting Flink JobManager..."
echo "=================================="

# Start Flink JobManager
/docker-entrypoint.sh jobmanager &

echo "Waiting 20 seconds for Flink..."
sleep 20

echo "Submitting Patient Processor Job..."

flink run -py /opt/flink/jobs/patient_processor.py

echo "Flink Job Submitted Successfully."

# Keep container alive
wait