# Server for relay
import multiprocessing
import socket
from _socket import SHUT_RDWR
import struct
import time

GLOVE = 0
VEST = 1
GUN = 2
SHOT_FIRED = 188
SHOT_HIT = 161


class RelayLaptop(multiprocessing.Process):
    def __init__(self, port_num, group_id, relay_pred, relay_eval, has_terminated):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_addr = ('', port_num)  # localhost
        self.socket.bind(self.soc_addr)
        self.relay_pred = relay_pred
        self.relay_eval = relay_eval
        self.group_id = group_id
        self.conn = None
        self.has_terminated = has_terminated

    def setup_connection(self):
        try:
            # 2 is the number of unaccepted connections that the system will allow before refusing new connections
            self.socket.listen(1)
            # Wait for a connection
            print('[Relay]Waiting for a connection')
            self.conn, client_address = self.socket.accept()
            print('[Relay]Connection from', client_address)
            return client_address
        except ConnectionRefusedError:
            print("[Relay] Cannot connect to Ultra96")
        except Exception as e:
            print(e)

    def run(self):
        self.setup_connection()
        while not self.has_terminated.value:
            # max packt sender + 6 extracted features (8 each)
            s = time.perf_counter()
            byte_msg = self.conn.recv(49)
            if byte_msg[0] == GLOVE:
                # print(float.fromhex(byte_msg[1:2]))
                extracted_features = []
                for i in range(1, 49, 8):
                    extracted_features.append(
                        struct.unpack('<d', byte_msg[i:i+8])[0])
                self.relay_pred.send(
                    (extracted_features, 0))  # 0 is p1, 1 is p2 (need to change)
            elif byte_msg[0] == VEST and byte_msg[3] == SHOT_HIT:
                self.relay_eval.send(("vest", 1))
            elif byte_msg[0] == GUN and byte_msg[3] == SHOT_FIRED:
                self.relay_eval.send(("shoot", 0))
            else:
                print("Invalid data received")

    def logout(self):
        self.has_terminated.value = True
        try:
            self.conn.shutdown(SHUT_RDWR)
            self.conn.close()
        except OSError:
            # connection already closed
            pass
        print("[Relay] Connection closed")
