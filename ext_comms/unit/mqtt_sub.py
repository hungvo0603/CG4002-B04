# Subscriber
# python3.6

import random
import threading
from paho.mqtt import client as mqtt_client


broker = 'broker.emqx.io'
port = 1883
topic = "cg4002/4/test"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'


class Subscriber(threading.Thread):
    def __init__(self, topic, client_id):
        super().__init__()
        self.topic = topic
        self.client_id = client_id
        self.client = self.connect_mqtt()

    def connect_mqtt(self):
        def on_connect(client, broker, port, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
    #     client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def subscribe_topic(self):
        def on_message(client, userdata, msg):
            print(
                f"[Sub] Received message: `{msg.payload.decode()}` from `{msg.topic}` topic")
            if msg.payload.decode() == "exit":
                self.client.disconnect()

        self.client.subscribe(topic)
        self.client.on_message = on_message

    def loop_forever(self):
        self.client.loop_forever()


if __name__ == '__main__':
    sub = Subscriber(topic, client_id)
    sub.subscribe_topic()
    sub.loop_forever()
