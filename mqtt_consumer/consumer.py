import json
import paho.mqtt.client as mqtt

from mqtt_consumer.model.sensor_record import SensorRecord
from mqtt_consumer.storage.sqlite_writer import SQLiteWriter

BROKER = "localhost"
PORT = 1883
TOPIC = "sensor/#"


def on_connect(client, userdata, flags, rc):
    print("MQTT Consumer connected")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        record = SensorRecord.from_dict(payload)
        SQLiteWriter.save(record)
        print(f"Saved: {record}")
    except Exception as e:
        print("Error handling message:", e)


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()