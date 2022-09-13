# Processes:
# - ml model, comm visualiser, comm eval, comm relay
import threading
import socket
import sys


class Server(threading.Thread):
    def __init__(self, port_num, group_id):
        super().__init__()  # init parent (Thread)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_addr = ('', port_num)  # localhost
        self.socket.bind(self.soc_addr)
        self.group_id = group_id
        self.conn = None

    def setup_connection(self):
        # 1 is the number of unaccepted connections that the system will allow before refusing new connections
        self.socket.listen(1)

        # Wait for a connection
        print('Waiting for a connection')
        self.conn, client_address = self.socket.accept()
        print('connection from', client_address)

    def end_client_connection(self):
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except OSError:
            # Already closed
            pass

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

        except ConnectionResetError:
            print('Connection Reset')
            self.end_client_connection()
        return message

    def run(self):

        self.setup_connection()
        message = ""

        while message != "logout":
            # received data from eval_server is unencrypted
            message = self.receive_data()
            print("Received message: ", message)

        self.end_client_connection()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('[Client] Invalid number of arguments')
        sys.exit()

    port_num = int(sys.argv[1])
    group_id = int(sys.argv[2])

    my_server = Server(port_num, group_id)
    my_server.start()

    my_server.join()
