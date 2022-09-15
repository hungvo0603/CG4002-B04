# Processes:
# - ml model, comm visualiser, comm eval, comm relay

import random as rd
from Crypto.Cipher import AES
from paho.mqtt import client as mqtt_client
from Crypto import Random
import threading
import base64
import socket
import sys
import json
import time

# p1 100 grenade 1 1 1 1 1 1

mqtt_broker = 'broker.emqx.io'  # Public broker
mqtt_port = 1883

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
move_res_lock = threading.Lock()
move_res_buffer = []  # predicted action
move_data_lock = threading.Lock()
move_data_buffer = []  # data relayed from internal comms
eval_lock = threading.Lock()
eval_buffer = []  # game state
viz_send_lock = threading.Lock()
viz_send_buffer = []  # game state
viz_recv_lock = threading.Lock()
viz_recv_buffer = []  # bool value for grenade hit


def read_data(buffer, lock):
    lock.acquire()
    data = buffer.pop(0)
    lock.release()
    return data


def input_data(buffer, lock, data):
    lock.acquire()
    buffer.append(data)
    lock.release()


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
            if len(move_data_buffer):
                data = read_data(move_data_buffer, move_data_lock)
                print("[MovePredictor]Received data: ", data)
                action = self.pred_action(data)
                print("[MovePredictor]Generated action: ", action)
                input_data(move_res_buffer, move_res_lock, action)


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
            if len(viz_send_buffer):
                state = read_data(viz_send_buffer, viz_send_lock)
                message = json.dumps(state)
                result = self.client.publish(self.topic, message)
                print("[Mqtt]Published data: ", message)
                status = result[0]
                if status == 0:
                    print("[Mqtt]Published data: ", message)
                else:
                    print("[Mqtt]Failed to send message: ", message)

    def subscribe(self):
        def on_message(client, userdata, msg):
            input_data(viz_recv_buffer, viz_recv_lock, msg.payload.decode())
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

        action = ""

        while action != "logout":
            if len(eval_buffer):
                # message = input(
                #     "[Client] Enter state [player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield]: ")

                state = read_data(eval_buffer, eval_lock)

                # player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield = read_data(
                #     eval_buffer, eval_lock)

                # self.send_data(player_num, hp, action, bullets, grenades,
                #                shield_time, shield_health, num_deaths, num_shield)

                self.send_data(state)

                # received data from eval_server is unencrypted ground truth
                data = self.receive_data()
                true_state = json.loads(data)
                input_state(true_state)

                # send ground truth to visualiser
                true_state["action"] = ""
                input_data(viz_send_buffer, viz_send_lock, true_state)

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

    # Implementation from https://github.com/pycrypto/pycrypto/blob/master/lib/Crypto/Util/Padding.py
    def pad_data(self, data_to_pad, block_size):
        padding_len = block_size - len(data_to_pad) % block_size
        padding = bytes([padding_len])*padding_len
        return bytes(data_to_pad, encoding="utf8") + padding

    def encrypt_message(self, state):
        # AES.block_size = 16 (default)
        # padding with 0x02 (start of text)
        message = json.dumps(state)
        print("[Eval server] Raw message:", message)
        padded_msg = self.pad_data(message, AES.block_size)
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

    # def send_data(self, player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield):
    #     message = self.jsonify_state(
    #         player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield)
    #     encrypted_text = self.encrypt_message(message)
    #     # _ is used as delimiter between len and content
    #     packet_size = (str(len(encrypted_text)) + '_').encode("utf-8")
    #     self.conn.sendall(packet_size)
    #     self.conn.sendall(encrypted_text)
    #     print("[Eval server] Sent encrypted data:", encrypted_text)

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
            # received data from eval_server is unencrypted
            message = self.receive_data()

            input_data(move_data_buffer, move_data_lock, message)
            # do sth to data
            # time.sleep(2)

            # self.send_data(message)
            # print("[Client] Sent data:", message)

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
    # eval_ip, eval_port = tunnel_addr  # added
    conn_eval = Client(eval_ip, eval_port, group_id, secret_key)
    conn_eval.start()

    # Connection to visualizer
    recv_client = Mqtt("cg4002/4/u96_viz2", "u96_recv")
    pub_client = Mqtt("cg4002/4/viz_u962", "u96_pub")

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
        if len(move_res_buffer):
            action = read_data(move_res_buffer, move_res_lock)
            print("[Game engine] Received action:", action)

            state = read_state()

            # do sth based on action
            state["p1"]["action"] = action

            input_state(state)
            print("[Game engine] Resulting state:", state)

            if action != "grenade":
                input_data(eval_buffer, eval_lock, state)
                print("[Game engine] Sent to eval:", state)

            input_data(viz_send_buffer, viz_send_lock, state)
            print("[Game engine] Sent to visualiser:", state)

        if len(viz_recv_buffer):
            # Visualizer sends player that is hit by grenade
            player_hit = read_data(viz_recv_buffer, viz_recv_lock)
            print("[Game engine] Received from visualiser:", state)
            state = read_state()
            if player_hit != "none":
                # minus health based on grenade hit
                state[player_hit]["hp"] -= 20

            input_state(state)
            input_data(eval_buffer, eval_lock, state)
            print("[Game engine] Sent to curr state and eval:", state)

    pub_client.terminate()
    recv_client.terminate()
