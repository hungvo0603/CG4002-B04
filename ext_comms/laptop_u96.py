import threading
import time
import sys
import socket
import json
import os
import dotenv
import sshtunnel

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

relay_lock = threading.Lock()
relay_buffer = []  # bool value for grenade hit

# Load environment variables
dotenv.load_dotenv()
XILINX_HOST = os.getenv('XILINX_HOST')
XILINX_PWD = os.getenv('XILINX_PWD')
SUNFIRE_USER = os.getenv('SUNFIRE_USER')
SUNFIRE_PWD = os.getenv('SUNFIRE_PWD')
SUNFIRE_HOST = 'stu.comp.nus.edu.sg'


class Client(threading.Thread):
    def __init__(self, local_port, remote_port, group_id):
        super().__init__()  # init parent (Thread)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.local_port = local_port
        self.remote_port = remote_port
        self.group_id = group_id
        # Open tunnel and connect
        self.tunnel_dest = self.create_tunnel()
        self.conn.connect(self.tunnel_dest)
        self.daemon = True

    def run(self):
        message = ""
        while message != "logout":
            if len(relay_buffer):
                relay_lock.acquire()
                message = relay_buffer.pop(0)
                relay_lock.release()
                self.send_data(message)

        self.end_client_connection()

    def create_tunnel(self):
        # u96 to sunfire
        tunnel_sunfire = sshtunnel.open_tunnel(
            ssh_address_or_host=(SUNFIRE_HOST, 22),  # gateway
            remote_bind_address=(XILINX_HOST, 22),
            ssh_username=SUNFIRE_USER,
            ssh_password=SUNFIRE_PWD
        )
        tunnel_sunfire.start()
        print(tunnel_sunfire.tunnel_is_up, flush=True)

        # relay to u96 (this part is sort of like creating another tunnel on curr machine to pass through the xilinx pwd)
        tunnel_xilinx = sshtunnel.open_tunnel(
            ssh_address_or_host=('localhost', tunnel_sunfire.local_bind_port),
            remote_bind_address=('localhost', self.remote_port),
            ssh_username="xilinx",
            ssh_password=XILINX_PWD,
            local_bind_address=('localhost', self.local_port)
        )
        tunnel_xilinx.start()
        print(tunnel_xilinx.tunnel_is_up, flush=True)
        return tunnel_xilinx.local_bind_address

    # def jsonify_state(self, player_num, hp, action, bullets, grenades, shield_time, shield_health, num_deaths, num_shield):
    #     curr_state[player_num] = {
    #         "hp": hp,
    #         "action": action,
    #         "bullets": bullets,
    #         "grenades": grenades,
    #         "shield_time": shield_time,
    #         "shield_health": shield_health,
    #         "num_deaths": num_deaths,
    #         "num_shield": num_shield
    #     }
    #     return json.dumps(curr_state)

    def end_client_connection(self):
        self.conn.close()

    def send_data(self, message):
        # _ is used as delimiter between len and content
        packet_size = (str(len(message)) + '_').encode("utf-8")
        self.conn.sendall(packet_size)
        self.conn.sendall(bytes(str(message), encoding="utf8"))

    # def receive_data(self):  # blocking call
    #     try:
    #         # recv length followed by '_' followed by cypher
    #         data = b''
    #         while not data.endswith(b'_'):
    #             _d = self.conn.recv(1)
    #             if not _d:
    #                 data = b''
    #                 break
    #             data += _d
    #         if len(data) == 0:
    #             print('no more data from the client')
    #             self.end_client_connection()

    #         data = data.decode("utf-8")
    #         length = int(data[:-1])

    #         data = b''
    #         while len(data) < length:
    #             _d = self.conn.recv(length - len(data))
    #             if not _d:
    #                 data = b''
    #                 break
    #             data += _d
    #         if len(data) == 0:
    #             print('no more data from the client')
    #             self.end_client_connection()
    #         message = data.decode("utf8")  # Decode raw bytes to UTF-8

    #         print("[Client] decoded_text:", message)

        # except ConnectionResetError:
        #     print('Connection Reset')
        #     self.end_client_connection()
        # return message


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('[Client] Invalid number of arguments')
        sys.exit()

    local_port = int(sys.argv[1])
    remote_port = int(sys.argv[2])
    group_id = sys.argv[3]

    conn_u96 = Client(local_port, remote_port, group_id)
    conn_u96.start()

    # Simulate receive data from bettles
    message = ""

    while message != "logout":
        message = input("[Client] Enter message: ")
        relay_lock.acquire()
        relay_buffer.append(message)
        relay_lock.release()

    conn_u96.join()
