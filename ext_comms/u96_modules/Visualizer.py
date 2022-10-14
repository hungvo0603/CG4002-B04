import multiprocessing
from paho.mqtt import client as mqtt_client
import socket
import threading
import multiprocessing

mqtt_broker = "test.mosquitto.org"  # 'broker.emqx.io'  # Public broker
mqtt_port = 1883

MQTT_PUB = "cg4002/4/viz_u9620"
MQTT_SUB = "cg4002/4/u96_viz20"


class Visualizer(multiprocessing.Process):
    def __init__(self, viz_eval):
        self.pub = Mqtt(MQTT_PUB)
        self.sub = Mqtt(MQTT_SUB)
        self.viz_eval = viz_eval
        self.has_terminated = False

    def publish(self):
        while not self.has_terminated:
            if self.viz_eval.pool():
                state = self.viz_eval.recv()
                self.pub.publish(state)

    def subscribe(self):
        self.sub.subscribe()

    def terminate(self):
        self.has_terminated = True
        self.client.loop_stop()

    def start(self):
        pub_thread = threading.Thread(target=self.publish)
        self.subscribe()

        pub_thread.start()
        pub_thread.join()


class Mqtt():
    # Connection to visualiser
    def __init__(self, topic, viz_eval):
        super().__init__()
        self.topic = topic
        self.daemon = True
        self.conn = None
        self.viz_eval = viz_eval
        self.has_terminated = False
        self.connect_mqtt()

    def on_connect(client, broker, port, rc):
        if rc != 0:
            print("Failed to connect, return code: ", rc)

    def connect_mqtt(self):
        try:
            self.conn = mqtt_client.Client(clean_session=True)
            self.conn.on_connect = self.on_connect
            self.conn.connect(mqtt_broker, mqtt_port)
            print("[Mqtt] Connection established to ", self.topic)
        except:
            self.connect_mqtt()

    def publish(self, state):
        try:
            status = 1
            while status:
                result = self.client.publish(self.topic, state)
                status = result[0]
                if status:
                    print("[Mqtt Pub]Failed to send message, retrying")
        except (KeyboardInterrupt, socket.gaierror, ConnectionError):
            print("[Mqtt Pub]Keyboard Interrupt, terminating")
            self.has_terminated = True

    def parse_player(player):
        if player == "p1":
            return 0
        return 1

    def subscribe(self):
        def on_message(client, userdata, msg):
            player_hit = msg.payload.decode()
            if player_hit != "none":
                self.viz_eval.send(self.parse_player(player_hit))
            print("[Mqtt]Received data: ", player_hit)

        self.conn.on_message = on_message
        self.conn.subscribe(self.topic)
        self.conn.loop_start()

    def terminate(self):
        # dont need to unsubs because clean session is true
        self.conn.disconnect()
        self.conn.loop_stop()
