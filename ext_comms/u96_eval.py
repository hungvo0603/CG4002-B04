# TODO:
# remove env xilinx host (input or env)
# try out client remote

from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto import Random
import threading
import sys
import base64
import socket
import json
import os
import dotenv

# python laptop_u96.py 127.0.0.1 1 4 1234567890123456 secret_key (16-digit)
# p1 100 grenade 1 1 1 1 1 1

# Player JSON format
# {
# 	"hp":           integer value of current player health,
# 	"action":       string representing the current action performed by the player

# Taking values from "grenade, reload, shoot, logout, shield",
# 	"bullets":      integer value of number of bullets left in the magazine,
# 	"grenades":     integer value of number of grenades left,
# 	"shield_time": 	integer value of number of seconds remaining in the shield,
# 	"shield_health": integer value of amount damage the shield can take,
# 	"num_deaths":   integer value of number of times the player died,
# 	"num_shield":   integer value of number of shield left
# }

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

# Load environment variables
dotenv.load_dotenv()
XILINX_HOST = os.getenv('XILINX_HOST')
SUNFIRE_USER = os.getenv('SUNFIRE_USER')
SUNFIRE_PWD = os.getenv('SUNFIRE_PWD')
SUNFIRE_HOST = 'sunfire-r.comp.nus.edu.sg'


class Client(threading.Thread):
    def __init__(self, ip_addr, port_num, group_id, secret_key):
        super().__init__()  # init parent (Thread)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dest_address = (ip_addr, port_num)
        self.group_id = group_id
        self.secret_key = secret_key

        self.conn.connect(self.dest_address)
        print("[Client] Connection established to:", self.dest_address)

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

    def end_client_connection(self):
        self.conn.close()

    # def encrypt_message(self, message):
    #     print("[Client] message:", message)
    #     # AES.block_size = 16 (default)
    #     # padding with 0x02 (start of text)
    #     padded_msg = pad(bytes(message, "utf8"), AES.block_size)
    #     iv = Random.new().read(AES.block_size)  # generate iv
    #     aes_key = bytes(str(self.secret_key), encoding="utf8")
    #     cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    #     encrypted_text = base64.b64encode(
    #         iv + cipher.encrypt(padded_msg))  # encode with AES-128
    #     return encrypted_text

    def send_data(self, player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield):
        message = self.jsonify_state(
            player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield)
        encrypted_text = self.encrypt_message(message)
        # _ is used as delimiter between len and content
        packet_size = (str(len(encrypted_text)) + '_').encode("utf-8")
        print("[Client] encrypted_text:", encrypted_text)
        self.conn.sendall(packet_size)
        self.conn.sendall(encrypted_text)

    def receive_data(self, is_encrypted):  # blocking call
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

            if is_encrypted:
                message = self.decrypt_message(message)

            print("[Client] decoded_text:", message)
            ### Update game state :D ###

        except ConnectionResetError:
            print('Connection Reset')
            self.end_client_connection()
        return message

    def decrypt_message(self, encrypted_text):
        decoded_message = base64.b64decode(encrypted_text)
        iv = decoded_message[:AES.block_size]  # extract iv
        secret_key_encoded = bytes(str(self.secret_key), encoding="utf8")

        decipher = AES.new(secret_key_encoded, AES.MODE_CBC, iv)
        message = decipher.decrypt(decoded_message[AES.block_size:])  # decrypt
        message = unpad(message, AES.block_size).decode('utf8')  # unpad
        print("[Server] message:", message)
        return message


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('[Client] Invalid number of arguments')
        print(
            'python no_tunnel.py [IP address] [Port] [groupID] [secret key]')
        sys.exit()

    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])
    group_id = sys.argv[3]
    secret_key = sys.argv[4]

    my_client = Client(ip_addr, port_num, group_id, secret_key)

    curr_state = INITIAL_STATE
    action = ""

    while action != "logout":
        message = input(
            "[Client] Enter state [player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield]: ")
        player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield = message.split(
            " ")
        my_client.send_data(player_num, hp, action, bullets, grenades,
                            shield_time, shield_health, num_deaths, num_shield)
        print("[Client] Sent data:", message)

        # received data from eval_server is unencrypted
        my_client.receive_data(False)

    my_client.end_client_connection()
