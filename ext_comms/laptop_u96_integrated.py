# Todo: try out with beetle
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
import struct
import threading
import time
import sys
import socket
import os
import dotenv
import sshtunnel
from queue import Queue
import time
import struct

relay_buffer = Queue()

# Load environment variables
dotenv.load_dotenv()
XILINX_HOST = os.getenv('XILINX_HOST')
XILINX_PWD = os.getenv('XILINX_PWD')
SUNFIRE_USER = os.getenv('SUNFIRE_USER')
SUNFIRE_PWD = os.getenv('SUNFIRE_PWD')
SUNFIRE_HOST = 'stu.comp.nus.edu.sg'

SYN = 'S'
ACK = 'A'
NAK = 'N'

# Need to send ACK and SYN as 20 byte packets as well
packetOne_len = 20
oneByte_data_len = 4

counter = 0  # for timing purposes
fragmentedCounter = 0
droppedCounter = 0
partialpacket = False

startTime = time.time()


class ScannerDelegate(DefaultDelegate):

    def __init__(self, char):
        DefaultDelegate.__init__(self)
        self.char = char
        self.done_handshake = False
        self.SeqID = 0

    def handleNotification(self, cHandle, data):

        if self.done_handshake:  # when handshake is done
            full_packet = True
            pkt = bytearray(data)

            # print("Packet: " + str(pkt)) #to see the packet

            if pkt[2] == 0:
                correct_pkt = checksum(pkt)
                self.SeqID = (self.SeqID + 1) & 0xFF

                if(correct_pkt):
                    self.packetOne = bytearray(pkt[0:15])
                else:
                    self.char.write(str.encode(NAK))
                    print("Failed checksum")

            elif pkt[2] == 1:
                full_packet = False
                correct_pkt = checksum(pkt)
                self.SeqID = (self.SeqID + 1) & 0xFF

                if(correct_pkt):
                    self.packetTwo = bytearray(pkt[0:15])
                else:
                    self.char.write(str.encode(NAK))
                    print("Failed checksum")

            if(not full_packet and (self.packetOne[1] + 1 == self.packetTwo[1])):
                relay_buffer.put(self.packetOne + self.packetTwo[3:15])
                # print("combined")
            # else:
            #     print("1st: " + str(self.packetOne[1]) + "2nd: " + str(self.packetTwo[3:14]))

        # Received ACK from bluno beetle after SYN is sent
        elif data == str.encode(ACK):
            self.done_handshake = True
            self.char.write(str.encode(ACK))
        else:
            self.char.write(str.encode(SYN))


def timer():
    global startTime, counter, droppedCounter, fragmentedCounter
    if(time.time()-startTime >= 10):
        print("Data Rate for " + addr + " is: " + str(counter/10000) +
              " KB/sec")  # /1000 for KB and /10 to average in 10s
        startTime = time.time()
        counter = 0
        droppedCounter = 0
        fragmentedCounter = 0


def handshake(bluno, char, addr):
    done_handshake = False

    while done_handshake == False:
        if bluno.waitForNotifications(2.0):  # establish connection
            done_handshake = True
            print("Handshake done")
        else:
            char.write(str.encode(SYN))

    print(addr + " completed handshake")
    return done_handshake


def connection(addr):
    is_connected = False

    service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
    char_id = "0000dfb1-0000-1000-8000-00805f9b34fb"

    while is_connected == False:
        try:
            print("Establishing a connection with: " + addr)
            bluno = Peripheral(addr)

            # To turn on notifications
            service = bluno.getServiceByUUID(service_uuid)
            char = service.getCharacteristics(char_id)[0]

            bluno.setDelegate(ScannerDelegate(char))

            print("Bluno " + addr + " is connected")
            char.write(str.encode(SYN))
            return bluno, char
        except Exception:
            print("Encounter an error when connecting..")
            pass


def connection_thread(bluno, char, addr):
    bluno_handshake = False
    global droppedCounter
    while True:
        try:
            timer()
            if bluno_handshake:
                # establish connection, wait for 2s
                if bluno.waitForNotifications(2.0):
                    pass
                else:
                    bluno.disconnect()
                    print("Bluno " + addr + " has disconnected")
                    bluno_handshake = False
                    bluno, char = connection(addr)
                    droppedCounter = droppedCounter + 1
                    pass
            else:
                bluno_handshake = handshake(bluno, char, addr)

        except KeyboardInterrupt:
            bluno.disconnect()
            break
        except BTLEDisconnectError:
            print("Bluno " + addr + " has disconnected due to an error")
            bluno_handshake = False
            bluno, char = connection(addr)


def checksum(data):

    global counter

    checksum = 0
    pkt = bytearray(data)

    for digit in range(len(data) - 1):  # same way calc on beetle
        checksum = (checksum ^ data[digit]) & 0xFF

    if checksum == data[len(data)-1]:
        counter = counter + len(data) - 3  # minue beetleID, seqID and checksum
        return True
    else:
        return False


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
        # put display code here
        while True:
            try:
                pkt = relay_buffer.get()
                # print("Packet: " + str(pkt)) to see the packet
                print("Beetle ID: " + str(pkt[0]))
                print("Sequence ID: " + str(pkt[1]))
                print("gx: %.3f" % struct.unpack(
                    "<f", pkt[3:7]))  # little endian
                print("gy: %.3f" % struct.unpack("<f", pkt[7:11]))
                print("gZ: %.3f" % struct.unpack(
                    "<f", pkt[11:15]))  # little endian
                print("ax: %.3f" % struct.unpack("<f", pkt[15:19]))
                print("ay: %.3f" % struct.unpack("<f", pkt[19:23]))
                print("az: %.3f" % struct.unpack("<f", pkt[23:27]))
                # send data to server
                self.send_data(pkt)

            except KeyboardInterrupt:
                self.end_client_connection()
                break

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
            # changed from remote
            remote_bind_address=('localhost', self.remote_port),
            ssh_username="xilinx",
            ssh_password=XILINX_PWD,
            local_bind_address=('localhost', self.local_port)
        )
        tunnel_xilinx.start()
        print(tunnel_xilinx.tunnel_is_up, flush=True)
        return tunnel_xilinx.local_bind_address

    def end_client_connection(self):
        self.conn.close()

    def send_data(self, message):
        # _ is used as delimiter between len and content
        packet_size = (str(len(message)) + '_').encode("utf-8")
        self.conn.sendall(packet_size)
        self.conn.sendall(bytes(str(message), encoding="utf8"))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('[Client] Invalid number of arguments')
        sys.exit()

    local_port = int(sys.argv[1])
    remote_port = int(sys.argv[2])
    group_id = sys.argv[3]

    conn_u96 = Client(local_port, remote_port, group_id)
    conn_u96.start()

    # "d0:39:72:bf:bd:b6","d0:39:72:bf:c6:0d"
    addr_list = ["d0:39:72:bf:c1:a6"]
    bluno_list = []
    char_list = []

    for addr in addr_list:
        bluno, char = connection(addr)
        bluno_list.append(bluno)
        char_list.append(char)

    # zip creates [(bluno#, char#, addr#),..] for each bluno beetle
    for (b, c, a) in zip(bluno_list, char_list, addr_list):
        t = threading.Thread(target=connection_thread, args=(b, c, a, ))
        t.start()

    conn_u96.join()
