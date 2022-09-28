# Processes:
# - ml model, comm visualiser, comm eval, comm relay

import random as rd
from Crypto.Cipher import AES
from paho.mqtt import client as mqtt_client
from Crypto.Util.Padding import pad
from Crypto import Random
import threading
import base64
import socket
import sys
import json
from queue import Queue

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

state_lock = threading.Lock()
curr_state = INITIAL_STATE


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


class MovePredictor(threading.Thread):
    def __init__(self):
        super().__init__()  # init parent (Thread)
        self.daemon = True

    def pred_action(self, data):
        # Randomly generate action
        actions = ["grenade", "reload", "shoot", "shield"]
        return actions[rd.randint(0, 3)]

    # Machine learning model
    def run(self):
        action = ""
        while action != "logout":
            if not move_data_buffer.empty():
                data = move_data_buffer.get()
                print("[MovePredictor]Received data: ", data)
                action = self.pred_action(data)
                print("[MovePredictor]Generated action: ", action)
                move_res_buffer.put(action)


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
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)

        client.on_connect = on_connect
        client.connect(mqtt_broker, mqtt_port)
        return client

    def publish(self):
        while True:
            if not viz_send_buffer.empty():
                state = viz_send_buffer.get()
                message = json.dumps(state)
                result = self.client.publish(self.topic, message)
                status = result[0]
                if status == 0:
                    print("[Mqtt]Published data: ", message)
                else:
                    print("[Mqtt]Failed to send message: ", message)

    def subscribe(self):
        def on_message(client, userdata, msg):
            viz_recv_buffer.put(msg.payload.decode())
            print("[Mqtt]Received data: ", msg.payload.decode())

        self.client.on_message = on_message
        self.client.subscribe(self.topic)

    def terminate(self):
        self.client.unsubscribe()
        self.client.loop_stop()
        self.client.disconnect()


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
        action = ""

        while action != "logout":
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

        self.conn.close()

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
        self.conn.close()
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
        # 1 is the number of unaccepted connections that the system will allow before refusing new connections
        self.socket.listen(1)

        # Wait for a connection
        print('[Relay]Waiting for a connection')
        self.conn, client_address = self.socket.accept()
        print('[Relay]Connection from', client_address)
        return client_address

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

        # self.expecting_packet.clear() #if want to use event later -> sth like conditional variable

        # self.setup_connection()

        message = ""

        while True:
            try:
                # received data from eval_server is unencrypted
                message = self.receive_data()
                move_data_buffer.put(message)

            except Exception as e:
                self.conn.close()

    def end_client_connection(self):
        self.conn.close()
        print("[Eval server]Connection closed")


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
    recv_client = Mqtt("cg4002/4/u96_viz20", "adafd")
    pub_client = Mqtt("cg4002/4/viz_u9620", "fdgfg")

    # Receive messages
    recv_client.subscribe()
    recv_client.client.loop_start()

    pub_thread = threading.Thread(target=pub_client.publish, daemon=True)
    pub_thread.start()

    # ML stuff
    model_pred = MovePredictor()
    model_pred.start()

    # Game engine (main thread)
    action = ""
    while action != "logout":
        if not move_res_buffer.empty():
            action = move_res_buffer.get()
            print("[Game engine] Received action:", action)

            state = read_state()

            # do sth based on action ["grenade", "reload", "shoot", "shield"]
            state["p1"]["action"] = action

            input_state(state)
            print("[Game engine] Resulting state:", state)

            if action != "grenade":
                eval_buffer.put(state)
                print("[Game engine] Sent to eval:", state)

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
                state[player_hit]["hp"] -= 20

            input_state(state)
            eval_buffer.put(state)
            print("[Game engine] Sent to curr state and eval:", state)

    pub_client.terminate()
    recv_client.terminate()
