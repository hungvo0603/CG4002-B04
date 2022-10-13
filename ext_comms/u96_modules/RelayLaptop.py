# Server for relay
import multiprocessing
import socket
from _socket import SHUT_RDWR
import struct

# pkt[0]: type of sender (0: imu sensor (glove)-> give ml, 1: ir receiver(vest), 2: shoot(gun))
GLOVE = '0'
VEST = '1'
GUN = '2'
SHOT_FIRED = '188'
SHOT_HIT = '161'


class RelayLaptop(multiprocessing.Process):
    def __init__(self, port_num, group_id, move_data_buffer_in, move_res_buffer_in):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_addr = ('', port_num)  # localhost
        self.socket.bind(self.soc_addr)
        self.move_data_buffer_in = move_data_buffer_in
        self.move_res_buffer_in = move_res_buffer_in
        self.group_id = group_id
        self.conn = None
        self.has_terminated = False

    def setup_connection(self):
        try:
            # 1 is the number of unaccepted connections that the system will allow before refusing new connections
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
        while not self.has_terminated:
            # max packt sender + 6 extracted features
            message = self.conn.recv(7)  # fixed 7 bit data
            print("[Relay] Received message:", message)
            byte_msg = bytearray(message)

            if str(byte_msg[0]) == GLOVE:
                extracted_features = []
                extracted_features.append(struct.unpack("<f", byte_msg[1]))
                extracted_features.append(struct.unpack("<f", byte_msg[2]))
                extracted_features.append(struct.unpack("<f", byte_msg[3]))
                extracted_features.append(struct.unpack("<f", byte_msg[4]))
                extracted_features.append(struct.unpack("<f", byte_msg[5]))
                extracted_features.append(struct.unpack("<f", byte_msg[6]))
                self.move_data_buffer_in.send(extracted_features)
            elif str(byte_msg[0]) == VEST and str(byte_msg[3]) == SHOT_HIT:
                self.move_res_buffer_in.send("vest")
            elif str(byte_msg[0]) == GUN and str(byte_msg[3]) == SHOT_FIRED:
                self.move_res_buffer_in.send("shoot")
            else:
                print("Invalid data received")

    def logout(self):
        self.has_terminated = True
        try:
            self.conn.shutdown(SHUT_RDWR)
            self.conn.close()
        except OSError:
            # connection already closed
            pass
        print("[Relay] Connection closed")
