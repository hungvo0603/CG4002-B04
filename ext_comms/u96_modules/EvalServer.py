from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto import Random
import multiprocessing
import socket
import json
import base64
from _socket import SHUT_RDWR


class EvalServer(multiprocessing.Process):
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

    # def jsonify_state(self, player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield):
    #     state = read_state()
    #     state[player_num] = {
    #         "hp": hp,
    #         "action": action,
    #         "bullets": bullets,
    #         "grenades": grenades,
    #         "shield_time": shield_time,
    #         "shield_health": shield_health,
    #         "num_deaths": num_deaths,
    #         "num_shield": num_shield
    #     }
    #     input_state(state)
    #     return json.dumps(state)

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
        # print("[Eval server] Sent encrypted data:", encrypted_text)

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
