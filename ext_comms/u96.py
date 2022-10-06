# Processes:
# - ml model, comm visualiser, comm eval, comm relay
# Todo:
# debug mqtt connection error -> temp failure in name resolution, broken pipe -> relay
# vest send data to is_hit -> shoot needs to have time window for the vest data to come in (if timeout -> miss bullet)
# 2 player -> wait for both player action to come before send to eval/do anything (cant have player with "none" action)
# 2 player: can either have shield first then damage or vice versa
# pkt[0]: type of sender (0: imu sensor (glove)-> give ml, 1: ir receiver(vest), 2: shoot(gun))
# need to send data to viz cause got test wo eval server (if action is invalid dont send to viz)
# continue action after the broken pipe nonetype error or the mqqt temp name resolution error too

import random as rd
from struct import unpack
from Crypto.Cipher import AES
from paho.mqtt import client as mqtt_client
from Crypto.Util.Padding import pad
from Crypto import Random
import threading
import base64
import socket
from _socket import SHUT_RDWR
import sys
import json
from queue import Queue
import uuid
import time

mqtt_broker = 'broker.emqx.io'  # Public broker
mqtt_port = 1883

DEFAULT_STATE = {
    "hp": 100,
    "action": "none",
    "bullets": 6,
    "grenades": 2,
    "shield_time": 0,
    "shield_health": 0,
    "num_deaths": 0,
    "num_shield": 3
}

INITIAL_STATE = {
    "p1": DEFAULT_STATE,
    "p2": DEFAULT_STATE
}

BULLET_DAMAGE = 10
GRENADE_DAMAGE = 30
SHIELD_TIME = 10
SHIELD_HEALTH = 30

# pkt[0]: type of sender (0: imu sensor (glove)-> give ml, 1: ir receiver(vest), 2: shoot(gun))
GLOVE = 0
VEST = 1
GUN = 2

state_lock = threading.Lock()
curr_state = INITIAL_STATE
shield_start = {"p1": None, "p2": None}  # both player has no shield


def read_state():
    state_lock.acquire()
    data = curr_state
    state_lock.release()
    return data


def input_state(data):
    global curr_state
    state_lock.acquire()
    curr_state = data
    state_lock.release()


# Data buffer
move_res_buffer = Queue()  # predicted action
move_data_buffer = Queue()  # data relayed from internal comms
eval_buffer = Queue()  # game state
viz_send_buffer = Queue()  # game state
viz_recv_buffer = Queue()  # bool value for grenade hit

# Connections
has_terminated = False
# Temporary
action_count = 0


class MovePredictor(threading.Thread):
    def __init__(self):
        super().__init__()  # init parent (Thread)
        self.daemon = True

    def pred_action(self, data):
        # Randomly generate action
        actions = ["shoot", "grenade", "reload", "shield"]
        global action_count
        action_count += 1
        return actions[action_count % 4]

    # Machine learning model
    def run(self):
        global has_terminated
        action = ""
        while action != "logout" and not has_terminated:
            try:
                if not move_data_buffer.empty():
                    data = move_data_buffer.get()
                    print("[MovePredictor]Received data: ", data)
                    unpacked_data = json.loads(data)

                    # Identify sender
                    if unpacked_data["sender"] == GLOVE:
                        action = self.pred_action(unpacked_data)
                    elif unpacked_data["sender"] == GUN:
                        action = "shoot"
                    elif unpacked_data["sender"] == VEST:
                        action = "vest"
                    else:
                        action = "none"
                        # if start of move:
                        # action = self.pred_action(unpacked_data)
                        # print("[MovePredictor]Generated action: ", action)
                        # move_res_buffer.put(action)

                    # action = self.pred_action(unpacked_data)
                    print("[MovePredictor]Generated action: ", action)
                    move_res_buffer.put(action)
            except KeyboardInterrupt:
                print("[MovePredictor]Keyboard Interrupt, terminating")
                has_terminated = True
                break

        has_terminated = True


class Mqtt(threading.Thread):
    # Connection to visualiser
    def __init__(self, topic, client_id):
        super().__init__()
        self.topic = topic
        self.client_id = client_id
        self.client = self.connect_mqtt()
        self.daemon = True

    def connect_mqtt(self):
        def on_connect(client, broker, port, rc):
            if rc != 0:
                print("Failed to connect, return code: ", rc)

        client = mqtt_client.Client(self.client_id, clean_session=True)

        client.on_connect = on_connect
        try:
            client.connect(mqtt_broker, mqtt_port)
        except:
            print("[Mqtt] Retry connection of ", self.topic)
            client.connect(mqtt_broker, mqtt_port)

        return client

    def publish(self):
        global has_terminated
        while True:
            try:
                if not viz_send_buffer.empty():
                    state = viz_send_buffer.get()
                    message = json.dumps(state)
                    result = self.client.publish(self.topic, message)
                    status = result[0]
                    if status == 0:
                        print("[Mqtt Pub]Published data: ", message)
                    else:
                        print("[Mqtt Pub]Failed to send message: ", message)

            except KeyboardInterrupt:
                print("[Mqtt Pub]Keyboard Interrupt, terminating")
                has_terminated = True
                break

    def subscribe(self):
        def on_message(client, userdata, msg):
            viz_recv_buffer.put(msg.payload.decode())
            print("[Mqtt]Received data: ", msg.payload.decode())

        self.client.on_message = on_message
        self.client.subscribe(self.topic)

    def terminate(self):
        # dont need to unsubs because clean session is true
        self.client.disconnect()
        self.client.loop_stop()


class Client(threading.Thread):
    # Client to eval_server
    def __init__(self, ip_addr, port_num, group_id, secret_key):
        super().__init__()  # init parent (Thread)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip_addr, port_num)
        self.group_id = group_id
        self.secret_key = secret_key
        self.daemon = True

    def run(self):
        self.conn.connect(self.server_address)
        print("[Eval server] Connection established to:", self.server_address)
        print("[Eval server] Copy to eval: ", self.secret_key)
        global has_terminated
        while not has_terminated:
            try:
                if not eval_buffer.empty():
                    state = eval_buffer.get()
                    self.send_data(state)

                    # received data from eval_server is unencrypted ground truth
                    data = self.receive_data()
                    true_state = json.loads(data)

                    input_state(true_state)

                    # send ground truth to visualiser
                    true_state["sender"] = "eval"
                    viz_send_buffer.put(true_state)
            except KeyboardInterrupt:
                print("[Eval server] Interrupt received, terminating")
                has_terminated = True
                break

    def jsonify_state(self, player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield):
        global curr_state
        state = read_state()
        state[player_num] = {
            "hp": hp,
            "action": action,
            "bullets": bullets,
            "grenades": grenades,
            "shield_time": shield_time,
            "shield_health": shield_health,
            "num_deaths": num_deaths,
            "num_shield": num_shield
        }
        input_state(state)
        return json.dumps(state)

    def encrypt_message(self, state):
        # AES.block_size = 16 (default)
        # padding with 0x02 (start of text)
        message = json.dumps(state)
        print("[Eval server] Raw message:", message)
        padded_msg = pad(bytes(message, "utf8"), AES.block_size)
        iv = Random.new().read(AES.block_size)  # generate iv
        aes_key = bytes(str(self.secret_key), encoding="utf8")
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        encrypted_text = base64.b64encode(
            iv + cipher.encrypt(padded_msg))  # encode with AES-128
        return encrypted_text

    def send_data(self, message):
        encrypted_text = self.encrypt_message(message)
        # _ is used as delimiter between len and content
        packet_size = (str(len(encrypted_text)) + '_').encode("utf-8")
        self.conn.sendall(packet_size)
        self.conn.sendall(encrypted_text)
        print("[Eval server] Sent encrypted data:", encrypted_text)

    def receive_data(self):  # blocking call
        try:
            # recv length followed by '_' followed by cypher
            data = b''
            while not data.endswith(b'_'):
                _d = self.conn.recv(1)
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                self.end_client_connection()

            data = data.decode("utf-8")
            length = int(data[:-1])

            data = b''
            while len(data) < length:
                _d = self.conn.recv(length - len(data))
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                self.end_client_connection()
            message = data.decode("utf8")  # Decode raw bytes to UTF-8

            print("[Eval server]Ground truth:", message)

        except ConnectionResetError:
            print('[Eval server]Connection Reset')
            self.end_client_connection()
        return message

    def end_client_connection(self):
        try:
            self.conn.shutdown(SHUT_RDWR)
            self.conn.close()
        except OSError:
            # connection already closed
            pass
        print("[Eval server]Connection closed")

# Server for relay


class Server(threading.Thread):
    def __init__(self, port_num, group_id):
        super().__init__()  # init parent (Thread)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_addr = ('', port_num)  # localhost
        self.socket.bind(self.soc_addr)
        self.group_id = group_id
        self.conn = None
        self.daemon = True

    def setup_connection(self):
        global has_terminated
        try:
            # 1 is the number of unaccepted connections that the system will allow before refusing new connections
            self.socket.listen(1)
            # Wait for a connection
            print('[Relay]Waiting for a connection')
            self.conn, client_address = self.socket.accept()
            print('[Relay]Connection from', client_address)
            return client_address
        except KeyboardInterrupt:
            print("[Relay] Keyboard interrupt, terminating")
            has_terminated = True

    # def stop(self):
    #     try:
    #         self.conn.shutdown(SHUT_RDWR)
    #         self.conn.close()
    #     except OSError:
    #         # connection already closed
    #         pass

    # def send_data(self, message):
    #     # encrypted_text = self.encrypt_message(message)
    #     encrypted_text = bytes(str(message), encoding="utf8")
    #     # _ is used as delimiter between len and content
    #     packet_size = (str(len(encrypted_text)) + '_').encode("utf-8")
    #     # print("[Client] encrypted_text:", encrypted_text)
    #     self.conn.sendall(packet_size)
    #     self.conn.sendall(encrypted_text)

    def receive_data(self):  # blocking call
        try:
            # recv length followed by '_' followed by cypher
            data = b''
            while not data.endswith(b'_'):
                _d = self.conn.recv(1)
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from the client')
                self.end_client_connection()

            data = data.decode("utf-8")
            length = int(data[:-1])

            data = b''
            while len(data) < length:
                _d = self.conn.recv(length - len(data))
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('[Relay] no more data from the client')
                self.client.end_client_connection()
            message = data.decode("utf8")  # Decode raw bytes to UTF-8

            print("[Relay] Received message:", message)

        except ConnectionResetError:
            print('[Relay]Connection Reset')
            self.client.end_client_connection()
        return message

    def run(self):
        global has_terminated
        while not has_terminated:
            try:
                # received data from eval_server is unencrypted
                message = self.receive_data()
                move_data_buffer.put(message)

            except KeyboardInterrupt:
                print("[Relay] Keyboard interrupt, terminating")
                has_terminated = True
                break

    def end_client_connection(self):
        try:
            self.conn.shutdown(SHUT_RDWR)
            self.conn.close()
        except OSError:
            # connection already closed
            pass
        print("[Relay]Connection closed")

# Game engine logic


def opp_player(player):
    if player == "p1":
        return "p2"
    else:
        return "p1"


def execute_action(player, action):
    state = read_state()
    other_player = opp_player(player)
    print("Player:", player, "Other Player:", other_player)
    # do sth based on action ["grenade", "reload", "shoot", "shield"]
    state[player]["action"] = action
    # state[other_player]["action"] = "none"

    # Recalculate shield time
    if shield_start[player]:
        time_elapsed = time.time() - shield_start[player]
        if time_elapsed >= SHIELD_TIME:
            shield_start[player] = None
            state[player]["shield_time"] = 0
            state[player]["shield_health"] = 0
        else:
            state[player]["shield_time"] = SHIELD_TIME - int(time_elapsed)

    if shield_start[other_player]:
        time_elapsed = time.time() - shield_start[other_player]
        if time_elapsed >= SHIELD_TIME:
            shield_start[other_player] = None
            state[other_player]["shield_time"] = 0
            state[other_player]["shield_health"] = 0
        else:
            state[other_player]["shield_time"] = SHIELD_TIME - \
                int(time_elapsed)

    # Execute action
    if action == "grenade":
        if state[player]["grenades"]:
            state[player]["grenades"] -= 1
        else:
            print("[Game engine] Cannot ", action, ". Only have ", state[player]
                  ["grenades"],  " grenade")
    elif action == "reload":
        if state[player]["bullets"] <= 0:
            state[player]["bullets"] = 6
        else:
            print("[Game engine] Cannot ", action, ". Still have ", state[player]
                  ["bullets"],  "bullets")
    elif action == "shoot":
        if state[player]["bullets"] <= 0:
            print("[Game engine] Cannot ", action, ".  Player has ", state[player]
                  ["bullets"],  "bullet")
        else:
            state[player]["bullets"] -= 1
            # Start timer to vest data to come

    elif action == "shield":
        if not shield_start[player] and state[player]["num_shield"]:
            state[player]["shield_time"] = SHIELD_TIME
            state[player]["shield_health"] = SHIELD_HEALTH
            state[player]["num_shield"] -= 1
            shield_start[player] = time.time()
        else:
            print("[Game engine] ", int(
                time.time() - shield_start[player]),  " seconds after previous shield")
    elif action == "vest":  # this vest is already opposite player's vest
        # ignore if no existing timer for shoot

        if state[player]["shield_health"]:
            state[player]["shield_health"] -= BULLET_DAMAGE

            if state[player]["shield_health"] < 0:
                state[player]["hp"] += state[player]["shield_health"]
                state[player]["shield_health"] = 0
        else:
            state[player]["hp"] -= BULLET_DAMAGE
    else:
        print("[Game engine] Unknown action: ", action)

    # Revive player if dead
    if state[other_player]["hp"] <= 0:
        state[other_player]["hp"] = 100
        state[other_player]["num_deaths"] += 1
        state[other_player]["num_shield"] = 3
        state[other_player]["grenades"] = 2

    if state[player]["hp"] <= 0:
        state[player]["hp"] = 100
        state[player]["num_deaths"] += 1
        state[player]["num_shield"] = 3
        state[player]["grenades"] = 2

    input_state(state)


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Invalid number of arguments')
        sys.exit()

    local_port = int(sys.argv[1])
    group_id = int(sys.argv[2])
    eval_port = int(sys.argv[3])
    eval_ip = sys.argv[4]
    secret_key = sys.argv[5]

    # Connection to relay
    conn_relay = Server(local_port, group_id)
    conn_relay.setup_connection()
    conn_relay.start()

    # Connection to eval_server
    conn_eval = Client(eval_ip, eval_port, group_id, secret_key)
    conn_eval.start()

    # Connection to visualizer
    recv_client = Mqtt("cg4002/4/u96_viz20", str(uuid.uuid4()))
    pub_client = Mqtt("cg4002/4/viz_u9620", str(uuid.uuid4()))

    # Receive messages
    recv_client.subscribe()
    recv_client.client.loop_start()

    # Publish messages
    pub_thread = threading.Thread(target=pub_client.publish, daemon=True)
    pub_thread.start()

    # ML stuff
    model_pred = MovePredictor()
    model_pred.start()

    state = read_state()
    # Game engine (main thread)
    while not has_terminated:
        try:
            if not move_res_buffer.empty():
                action = move_res_buffer.get()
                print("[Game engine] Received action:", action)
                execute_action("p1", action)
                print("[Game engine] Resulting state:", state)

                if action != "grenade":
                    eval_buffer.put(state)
                    print("[Game engine] Sent to eval:", state)
                else:
                    state["sender"] = "u96"
                    viz_send_buffer.put(state)
                    print("[Game engine] Sent to visualiser:", state)

            if not viz_recv_buffer.empty():
                # Visualizer sends player that is hit by grenade
                player_hit = viz_recv_buffer.get()
                print("[Game engine] Received from visualiser:", state)
                state = read_state()
                if player_hit != "none":
                    # minus health based on grenade hit
                    if state[player_hit]["shield_health"]:
                        state[player_hit]["shield_health"] -= GRENADE_DAMAGE

                        if state[player_hit]["shield_health"] < 0:
                            state[player_hit]["hp"] += state[player_hit]["shield_health"]
                            state[player_hit]["shield_health"] = 0
                    else:
                        state[player_hit]["hp"] -= GRENADE_DAMAGE

                input_state(state)
                eval_buffer.put(state)
                print("[Game engine] Sent to curr state and eval:", state)
        except KeyboardInterrupt:
            print("[Game Engine] Keyboard interrupt")
            has_terminated = True
            break

    # Terminate all connections
    if(conn_relay):
        conn_relay.end_client_connection()
        print(conn_relay)
    if(conn_eval):
        conn_eval.end_client_connection()
    if(recv_client):
        recv_client.terminate()
        print(recv_client)
    if(pub_client):
        pub_client.terminate()

    print("Program terminated, thanks for playing :D")
