# Mqtt for visualiser
# Key points:
# - Only subs to topic you wanna listen (if just pub dont need to subs))
import threading
from paho.mqtt import client as mqtt_client
import json

broker = 'broker.emqx.io'  # Public broker
port = 1883

DEFAULT_STATE = {
    "hp": 100,
    "action": "none",
    "bullets": 6,
    "grenades": 1,
    "shield_time": 0,
    "shield_health": 0,
    "num_deaths": 0,
    "num_shield": 3
}

INITIAL_STATE = {
    "p1": DEFAULT_STATE,
    "p2": DEFAULT_STATE
}

curr_state = INITIAL_STATE

# username = 'emqx'
# password = 'public'

input_buffer = []
is_logged_out = False


class Mqtt(threading.Thread):
    def __init__(self, topic, client_id):
        super().__init__()
        self.topic = topic
        self.client_id = client_id
        self.client = self.connect_mqtt()

    def connect_mqtt(self):
        def on_connect(client, broker, port, rc):
            if rc != 0:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
    #     client.username_pw_set(username, password)

        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def jsonify_state(self, player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield):
        curr_state[player_num] = {
            "hp": hp,
            "action": action,
            "bullets": bullets,
            "grenades": grenades,
            "shield_time": shield_time,
            "shield_health": shield_health,
            "num_deaths": num_deaths,
            "num_shield": num_shield
        }
        return json.dumps(curr_state)

    def publish(self):
        print("Publishing...")
        global is_logged_out

        while not is_logged_out:
            message = input(
                "[Pub] Enter state [player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield]: ")
            # player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield = message.split(
            #     " ")
            # self.send_data(player_num, hp, action, bullets, grenades,
            #                shield_time, shield_health, num_deaths, num_shield)

            result = self.client.publish(self.topic, message)
            status = result[0]
            if status == 0:
                print(f"Sent message [`{self.topic}`]: `{message}`")
            else:
                print(f"Failed to send message: `{message}`")

            if message == "logout":
                is_logged_out = True

    def subscribe(self):
        print("Subscribing...")

        def on_message(client, userdata, msg):
            input_buffer.append(msg.payload.decode())

        self.client.on_message = on_message
        self.client.subscribe(self.topic)

    def terminate(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == '__main__':
    print("Starting MQTT client...")
    recv_client = Mqtt("cg4002/4/u96_viz", "dssdaf")
    pub_client = Mqtt("cg4002/4/viz_u96", "sdfv")

    # Receive messages
    recv_client.subscribe()
    recv_client.client.loop_start()

    pub_thread = threading.Thread(target=pub_client.publish, daemon=True)
    pub_thread.start()

    message = ""
    while message != "logout" and not is_logged_out:
        if len(input_buffer):
            message = input_buffer.pop(0)
            print(f"Received message: ", message)

    print("Ending MQTT client...")
    is_logged_out = True
    pub_client.terminate()
    recv_client.terminate()
