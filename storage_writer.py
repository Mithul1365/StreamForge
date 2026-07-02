import json
import io
import pandas as pd
from kafka import KafkaConsumer
import boto3

# Connect to MinIO (S3-compatible storage)
s3_client = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

BUCKET_NAME = 'streamforge-data'
BATCH_SIZE = 10  # save after every 10 records (small for testing)

def save_batch_to_minio(batch, batch_number):
    # Convert list of dicts to a pandas DataFrame
    df = pd.DataFrame(batch)

    # Convert DataFrame to Parquet format in memory
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    # Upload to MinIO
    file_name = f"patient_data/batch_{batch_number}.parquet"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=buffer.getvalue())
    print(f"Saved batch {batch_number} to MinIO: {file_name} ({len(batch)} records)")

def main():
    consumer = KafkaConsumer(
        'patient-vitals-processed',
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("Storage writer started - reading from Kafka...\n")

    batch = []
    batch_number = 1

    for message in consumer:
        data = message.value
        batch.append(data)
        print(f"Collected: {data['patient_id']} ({len(batch)}/{BATCH_SIZE})")

        if len(batch) >= BATCH_SIZE:
            save_batch_to_minio(batch, batch_number)
            batch = []
            batch_number += 1

if __name__ == "__main__":
    main()