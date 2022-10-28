# Todo: add player num to packet
# Server for relay
import threading
import multiprocessing
import socket
from _socket import SHUT_RDWR
import struct
import time

GLOVE = 0
VEST = 1
GUN = 2
SHOT_FIRED_1 = 188
SHOT_HIT_1 = 161
SHOT_FIRED_2 = 182
SHOT_HIT_2 = 168
P1 = 0
P2 = 1
PACKET_SIZE = 50  # player + type + 6 floats
PORT_1 = 9000
PORT_2 = 10000


class RelayLaptop(multiprocessing.Process):
    def __init__(self, group_id, relay_pred, relay_eval, has_terminated, has_incoming_bullet_p1_in, has_incoming_bullet_p2_in):
        super().__init__()
        self.conn1 = Server(P1, PORT_1, group_id,
                            relay_pred, relay_eval, has_terminated, has_incoming_bullet_p1_in, SHOT_FIRED_1, SHOT_HIT_1)
        self.conn2 = Server(P2, PORT_2, group_id,
                            relay_pred, relay_eval, has_terminated, has_incoming_bullet_p2_in, SHOT_FIRED_2, SHOT_HIT_2)
        self.daemon = True
        # self.has_terminated = has_terminated

    def run(self):
        self.conn1.start()
        # conn2 run on main thread
        self.conn2.run()


class Server(threading.Thread):
    def __init__(self, player, port_num, group_id, relay_pred, relay_eval, has_terminated, has_incoming_bullet_in, shot_fired, shot_hit):
        super().__init__()
        self.player = player
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc_addr = ('', port_num)  # localhost
        self.socket.bind(self.soc_addr)
        self.relay_pred = relay_pred
        self.relay_eval = relay_eval
        self.has_incoming_bullet_in = has_incoming_bullet_in
        self.group_id = group_id
        self.conn = None
        self.has_terminated = has_terminated
        self.shot_fired = shot_fired
        self.shot_hit = shot_hit

    def setup_connection(self):
        try:
            # 1 is the number of unaccepted connections that the system will allow before refusing new connections
            self.socket.listen(1)
            # Wait for a connection
            print('[Relay]Waiting for a connection')
            self.conn, client_address = self.socket.accept()
            print('[Relay]Connection from', client_address,
                  ' ', self.player+1, "th connection")
        except ConnectionRefusedError:
            print("[Relay] Cannot connect to Ultra96")
        except Exception as e:
            print(e)

    def run(self):
        self.setup_connection()
        while not self.has_terminated.value:
            # max packt player + sender + 6 extracted features (8 each)
            # s = time.perf_counter()
            byte_msg = self.conn.recv(PACKET_SIZE)
            # print("[Relay] Received", len(byte_msg), "bytes")
            player = byte_msg[0]
            if byte_msg[1] == GLOVE:
                # print(float.fromhex(byte_msg[1:2]))
                extracted_features = []
                for i in range(2, PACKET_SIZE, 8):
                    extracted_features.append(
                        struct.unpack('<d', byte_msg[i:i+8])[0])
                self.relay_pred.send(
                    (extracted_features, player))  # 0 is p1, 1 is p2 (need to change)
                # print("[Relay] Send", len(extracted_features), "bytes")
            elif byte_msg[1] == VEST and byte_msg[4] == self.shot_hit:
                self.has_incoming_bullet_in.send(True)  # need to change
            elif byte_msg[1] == GUN and byte_msg[4] == self.shot_fired:
                self.relay_eval.send(("shoot", player))
            else:
                print("[Relay] Unknown packet: ", byte_msg)
                print("Invalid data received")
            time.sleep(0.1)  # sleep a bit after send

    def logout(self):
        self.has_terminated.value = True
        try:
            self.conn.shutdown(SHUT_RDWR)
            self.conn.close()
        except OSError:
            # connection already closed
            pass
        print("[Relay] Connection closed")
