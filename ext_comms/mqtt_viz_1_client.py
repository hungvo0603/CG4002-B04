# Mqtt for u96_viz

import sys
import threading
from paho.mqtt import client as mqtt_client
import time

broker = 'broker.emqx.io'  # Public broker
port = 1883


# username = 'emqx'
# password = 'public'

input_buffer = []
output_buffer = []


class Mqtt():
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

    def publish(self):
        print("Publishing...")
        message = ""
        while message != "logout":
            message = input("Enter message to publish: ")
            result = self.client.publish(self.topic, message)
            status = result[0]
            if status == 0:
                print(f"Sent message [`{self.topic}`]: `{message}`")
            else:
                print(f"Failed to send message: `{message}`")
        self.client.disconnect()

    def subscribe(self):
        print("Subscribing...")

        def on_message(client, userdata, msg):
            print(
                f"Received message: `{msg.payload.decode()}` from `{msg.topic}` topic")

            # time.sleep(2)  # do sth with data

            if msg.payload.decode() == "logout":
                self.client.loop_stop()
                self.client.disconnect()

        self.client.on_message = on_message
        self.client.subscribe(self.topic)
        self.client.loop()


if __name__ == '__main__':
    # Input client id (mqtt-[machine]-4)
    client_id = sys.argv[1]
    topic = "cg4002/4/u96_viz"

    client = Mqtt(topic, client_id)
    print("Starting MQTT client...")
    # Receive messages
    # client.subscribe()
    # client.publish()

    # print("Ending MQTT client...")
    recv_thread = threading.Thread(target=client.subscribe, daemon=True)
    recv_thread.start()
    # Publish messages
    pub_thread = threading.Thread(target=client.publish, daemon=True)
    pub_thread.start()

    recv_thread.join()
    pub_thread.join()
