#!/bin/bash

ROLE=$1

echo "=================================="
echo "Starting Flink Container"
echo "Role: $ROLE"
echo "=================================="

if [ "$ROLE" = "taskmanager" ]; then
    echo "Starting TaskManager..."
    exec /docker-entrypoint.sh taskmanager
fi

echo "Starting JobManager..."
/docker-entrypoint.sh jobmanager &

echo "Waiting for JobManager..."
sleep 30

echo "Submitting Patient Processor Job..."

flink run -py /opt/flink/jobs/patient_processor.py

echo "Job Submitted."

wait