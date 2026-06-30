from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
import json

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

consumer = FlinkKafkaConsumer(
    topics="patient-vitals",
    deserialization_schema=SimpleStringSchema(),
    properties={
        "bootstrap.servers": "kafka:9092",
        "group.id": "flink-processor"
    }
)

producer = FlinkKafkaProducer(
    topic="patient-vitals-processed",
    serialization_schema=SimpleStringSchema(),
    producer_config={
        "bootstrap.servers": "kafka:9092"
    }
)

def process(raw):

    print("RAW =", raw)

    try:
        data = json.loads(raw)

        status = "NORMAL"

        if int(data["heart_rate"]) > 120 or int(data["spo2"]) < 90:
            status = "CRITICAL"

        output = {
            "patient_id": data["patient_id"],
            "heart_rate": data["heart_rate"],
            "spo2": data["spo2"],
            "bp_systolic": data["bp_systolic"],
            "temperature": data["temperature"],
            "timestamp": data["timestamp"],
            "status": status
        }

        print("OUTPUT =", output)

        return json.dumps(output)

    except Exception as e:
        print(e)
        return ""

stream = env.add_source(consumer)

stream \
    .map(process, output_type=Types.STRING()) \
    .filter(lambda x: x != "") \
    .add_sink(producer)

env.execute("Patient Vitals Processor")