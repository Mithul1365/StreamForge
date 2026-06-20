from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
import json

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

kafka_consumer = FlinkKafkaConsumer(
    topics='patient-vitals',
    deserialization_schema=SimpleStringSchema(),
    properties={
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'flink-processor'
    }
)

kafka_producer = FlinkKafkaProducer(
    topic='patient-vitals-processed',
    serialization_schema=SimpleStringSchema(),
    producer_config={
        'bootstrap.servers': 'kafka:9092'
    }
)

def process_patient_data(raw_data):
    try:
        data = json.loads(raw_data)

        if not data.get('heart_rate') or not data.get('spo2'):
            return ""

        processed = {
            'patient_id': data['patient_id'],
            'heart_rate': int(data['heart_rate']),
            'spo2': int(data['spo2']),
            'bp_systolic': int(data['bp_systolic']),
            'temperature': float(data['temperature']),
            'timestamp': data['timestamp'],
            'status': 'CRITICAL' if data['heart_rate'] > 120
                      or data['spo2'] < 90
                      else 'NORMAL'
        }

        return json.dumps(processed)
    except Exception:
        return ""

stream = env.add_source(kafka_consumer)
processed_stream = stream.map(process_patient_data, output_type=Types.STRING()).filter(lambda x: x != "")
processed_stream.add_sink(kafka_producer)

env.execute("Patient Vitals Processor")