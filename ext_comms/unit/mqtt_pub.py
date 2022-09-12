# Mqtt (publisher)

import random
import threading
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'  # Public broker
port = 1883
topic = "cg4002/4/test"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'


class Publisher(threading.Thread):
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

    def publish(self, message):
        result = pub.client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"Sent message [`{topic}`]: `{message}`")
        else:
            print(f"Failed to send message to topic {topic}")


if __name__ == '__main__':
    pub = Publisher(topic, client_id)
    message = ""
    while message != "exit":
        message = input("[Pub] Enter message to publish: ")
        pub.publish(message)
