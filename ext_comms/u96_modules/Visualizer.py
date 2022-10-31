from paho.mqtt import client as mqtt_client
import json
import socket
import threading

mqtt_broker = 'broker.emqx.io'  # "test.mosquitto.org" Public broker
mqtt_port = 1883

MQTT_PUB = "cg4002/4/viz_u96"
MQTT_SUB = "cg4002/4/u96_viz"


class Visualizer():
    def __init__(self, eval_viz, viz_eval_p1, viz_eval_p2, has_terminated):
        self.pub = Mqtt(MQTT_PUB, viz_eval_p1, viz_eval_p2, has_terminated)
        self.sub = Mqtt(MQTT_SUB, viz_eval_p1, viz_eval_p2, has_terminated)
        self.eval_viz = eval_viz
        self.has_terminated = has_terminated

    def publish(self):
        while not self.has_terminated.value:
            state = self.eval_viz.get()
            # clear(self.viz_eval)
            # print("Visualizer state bef pub: ", state)
            self.pub.publish(json.dumps(state))

    def subscribe(self):
        self.sub.subscribe()

    def terminate(self):
        self.has_terminated.value = True
        self.sub.terminate()
        # self.pub.terminate()

    def start(self):
        pub_thread = threading.Thread(target=self.publish)
        self.subscribe()

        pub_thread.start()
        pub_thread.join()

        self.terminate()


class Mqtt():
    # Connection to visualiser
    def __init__(self, topic, p1_buffer, p2_buffer, has_terminated):
        super().__init__()
        self.topic = topic
        self.daemon = True
        self.conn = None
        self.p1_buffer = p1_buffer
        self.p2_buffer = p2_buffer
        self.has_terminated = has_terminated
        self.connect_mqtt()

    def connect_mqtt(self):
        def on_connect(client, broker, port, rc):
            if rc != 0:
                print("Failed to connect, return code: ", rc)

        try:
            self.conn = mqtt_client.Client()  # clean_session=True
            self.conn.on_connect = on_connect
            self.conn.connect(mqtt_broker, mqtt_port)
            print("[Mqtt] Connection established to ", self.topic)
        except:
            self.connect_mqtt()

    def publish(self, state):
        try:
            result = self.conn.publish(self.topic, state, qos=2)
            self.conn.loop(1, 1)  # loop to prevent mqtt from blocking
            print("[Mqtt]Sent data: ", state)
            # print("[Mqtt]Publish result: ", result)
            if result[0] != 0:
                print("Failed to publish, return code: ", result[0])
        except (KeyboardInterrupt, socket.gaierror, ConnectionError):
            print("[Mqtt Pub]Keyboard Interrupt, terminating")
            self.has_terminated.value = True

    def parse_player(player):
        if player == "p1":
            return 0
        return 1

    def subscribe(self):
        def on_message(client, userdata, msg):
            data = msg.payload.decode()
            print("[Mqtt]Received data: ", data)
            player, is_hit = data.split("-")
            if player == "p1":
                self.p1_buffer.put(is_hit == "hit")

            if player == "p2":
                self.p2_buffer.put(is_hit == "hit")

        self.conn.on_message = on_message
        self.conn.subscribe(self.topic, qos=2)
        self.conn.loop_start()

    def terminate(self):
        # dont need to unsubs because clean session is true
        self.conn.disconnect()
        self.conn.loop_stop()
