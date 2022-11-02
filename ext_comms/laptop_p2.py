from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
import numpy as np
import struct
import threading
import sys
import socket
import os
import dotenv
import sshtunnel
from queue import Queue
import struct
from statistics import median, mean, variance
from scipy.fftpack import fft
import time

relay_buffer = Queue()
has_closed = False
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
DISCONNECT = 1
CONNECT = 0
GLOVE = 0
VEST = 1
GUN = 2
SHOT_FIRED = 182
SHOT_HIT = 168
SOM_THRESHOLD = 0.8  # threshold value for start of move
PACKET_SIZE = 51  # player + type + 6 floats + disconnect
P1 = 0
P2 = 1
GUN_MAC = "D0:39:72:BF:C3:B8"
GLOVE_MAC = "78:DB:2F:BF:34:35"
VEST_MAC = "D0:39:72:BF:C6:0D"


# Need to send ACK and SYN as 20 byte packets as well
packetOne_len = 20
counter = 0  # for timing purposes
fragmentedCounter = 0
droppedCounter = 0
partialpacket = False
firstData = False
startTime = 0
start = False
dataCounter = 0
cycle = False
actual_cycle = False
has_connected = {
    GUN_MAC: False, GLOVE_MAC: False, VEST_MAC: False
}


class ScannerDelegate(DefaultDelegate):
    def __init__(self, char):
        DefaultDelegate.__init__(self)
        self.char = char
        self.done_handshake = False
        self.SeqID = 0

    def handleNotification(self, cHandle, data):
        if self.done_handshake:
            full_packet = True
            pkt = bytearray(data)
            # print("Packet: " + str(pkt))  # to see the packet
            if(len(pkt) == packetOne_len and pkt[0] == 0):
                # print("Glove Packet: " + str(pkt)) #to see the packet
                if pkt[2] == 0:
                    correct_pkt = checksum(pkt)
                    self.SeqID = (self.SeqID + 1) & 0xFF
                    if(correct_pkt):
                        self.packetOne = bytearray(pkt[0:15])
                        self.char.write(str.encode(ACK))
                    else:
                        self.char.write(str.encode(NAK))
                elif pkt[2] == 1:
                    full_packet = False
                    correct_pkt = checksum(pkt)
                    self.SeqID = (self.SeqID + 1) & 0xFF
                    if(correct_pkt):
                        self.packetTwo = bytearray(pkt[0:15])
                        self.char.write(str.encode(ACK))
                    else:
                        self.char.write(str.encode(NAK))
                if(not full_packet and (self.packetOne[1] + 1 == self.packetTwo[1])):
                    relay_buffer.put(self.packetOne + self.packetTwo[3:15])
            elif(len(pkt) == packetOne_len and pkt[0] == 1):
                # print("IR detected")
                correct_pkt = checksum(pkt)
                self.SeqID = (self.SeqID + 1) & 0xFF
                if(correct_pkt):
                    self.char.write(str.encode(ACK))
                    # print("Vest correct")
                    relay_buffer.put(pkt)
                else:
                    self.char.write(str.encode(NAK))
            elif(len(pkt) == packetOne_len and pkt[0] == 2):
                # print("Shot detected")
                correct_pkt = checksum(pkt)
                self.SeqID = (self.SeqID + 1) & 0xFF
                if(correct_pkt):
                    self.char.write(str.encode(ACK))
                    # print("Gun correct")
                    relay_buffer.put(pkt)
                else:
                    self.char.write(str.encode(NAK))
        # Received ACK from bluno beetle after SYN is sent
        elif data == str.encode(ACK):
            self.done_handshake = True
            self.char.write(str.encode(ACK))
        else:
            self.char.write(str.encode(SYN))


def handshake(bluno, char, addr):
    done_handshake = False
    while done_handshake == False:
        if bluno.waitForNotifications(2.0):  # establish connection
            done_handshake = True
            print("Handshake done")

        else:
            char.write(str.encode(SYN))

    print(addr + " completed handshake")

    if(addr == GUN_MAC and not has_connected[addr]):
        relay_buffer.put([GUN, CONNECT])
        print("Gun connected")
    elif(addr == GLOVE_MAC and not has_connected[addr]):
        print("Glove connected")
        relay_buffer.put([GLOVE, CONNECT])
    elif(addr == VEST_MAC and not has_connected[addr]):
        print("Green LED Vest connected")
        relay_buffer.put([VEST, CONNECT])
    has_connected[addr] = True
    return done_handshake


def connection(addr):
    is_connected = False
    service_uuid = "dfb0"
    char_id = "dfb1"
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
    global has_closed
    while not has_closed:
        try:
            if bluno_handshake:
                # establish connection, wait for 2s
                if bluno.waitForNotifications(2.0):
                    pass
                else:
                    bluno.disconnect()
                    print("Bluno " + addr + " disconnected")
                    bluno_handshake = False
                    bluno, char = connection(addr)
                    pass
            else:
                bluno_handshake = handshake(bluno, char, addr)
        except (KeyboardInterrupt, BrokenPipeError):
            has_closed = True
            bluno.disconnect()
            break
        except BTLEDisconnectError:
            if(addr == GUN_MAC and has_connected[addr]):
                relay_buffer.put([GUN, DISCONNECT])
                print("Gun disconnected")
            elif(addr == GLOVE_MAC and has_connected[addr]):
                print("Glove disconnected")
                relay_buffer.put([GLOVE, DISCONNECT])
            elif(addr == VEST_MAC and has_connected[addr]):
                print("Green LED Vest Disconnected")
                relay_buffer.put([VEST, DISCONNECT])
            has_connected[addr] = False
            bluno_handshake = False
            bluno, char = connection(addr)


def checksum(data):
    global counter
    checksum = 0
    # pkt = bytearray(data)
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
        self.daemon = True
        self.start_collection = False
        self.array_ax = []
        self.array_ay = []
        self.array_az = []
        self.array_gx = []
        self.array_gy = []
        self.array_gz = []

    def is_start_of_move(self):
        # might need to change
        print(np.max(self.array_ax) +
              np.max(self.array_ay) + np.max(self.array_az))
        return np.max(self.array_ax) + np.max(self.array_ay) + np.max(self.array_az) > SOM_THRESHOLD

    def extract_features(self, raw_data):
        extracted = []
        extracted = np.append(extracted, (np.min(raw_data)))
        extracted = np.append(extracted, (np.max(raw_data)))
        extracted = np.append(extracted, (sum(raw_data)))
        extracted = np.append(extracted, (median(raw_data)))
        extracted = np.append(extracted, (variance(raw_data)))
        raw_data = fft(raw_data)
        extracted = np.append(extracted, np.min(abs(raw_data)))
        extracted = np.append(extracted, np.max(abs(raw_data)))
        extracted = np.append(extracted, mean(abs(raw_data)))
        extracted = np.append(extracted, median(abs(raw_data)))
        extracted = np.append(extracted, variance(abs(raw_data)))
        return extracted

    def preprocess(self, pkt):  # look here
        self.array_ax.append(struct.unpack("<f", pkt[15:19])[0])
        self.array_ay.append(struct.unpack("<f", pkt[19:23])[0])
        self.array_az.append(struct.unpack("<f", pkt[23:27])[0])
        self.array_gx.append(struct.unpack("<f", pkt[3:7])[0])
        self.array_gy.append(struct.unpack("<f", pkt[7:11])[0])
        self.array_gz.append(struct.unpack("<f", pkt[11:15])[0])
        print(len(self.array_ax))
        # print(self.array_ax)
        if(not self.start_collection):
            if (len(self.array_ax) >= 5):
                print("Detecting start of move")
                if self.is_start_of_move():
                    print("Start of move detected")
                    time.sleep(1)
                    self.start_collection = True

                self.array_ax = []
                self.array_ay = []
                self.array_az = []
                self.array_gx = []
                self.array_gy = []
                self.array_gz = []
        else:
            if (len(self.array_ax) >= 40):
                print("40 data set collected")
                array_axayaz_gxgygz = []
                self.start_collection = False
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, self.extract_features(self.array_ax)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, self.extract_features(self.array_ay)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, self.extract_features(self.array_az)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, self.extract_features(self.array_gx)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, self.extract_features(self.array_gy)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, self.extract_features(self.array_gz)))
                array_axayaz_gxgygz = np.float_(array_axayaz_gxgygz)
                if (np.max(self.array_ax) > 0.5 and np.max(self.array_ay) > 0.5 and np.max(self.array_az) > 0.5):
                    print("action detected")
                    self.array_ax = []
                    self.array_ay = []
                    self.array_az = []
                    self.array_gx = []
                    self.array_gy = []
                    self.array_gz = []
                    return array_axayaz_gxgygz.tobytes()
                self.array_ax = []
                self.array_ay = []
                self.array_az = []
                self.array_gx = []
                self.array_gy = []
                self.array_gz = []

        return None

    def run(self):
        # Open tunnel and connect
        self.tunnel_dest = self.create_tunnel()
        self.conn.connect(self.tunnel_dest)
        global has_closed
        while not has_closed:
            try:
                pkt = relay_buffer.get()
                if(pkt[0] == GLOVE):
                    if len(pkt) == 2 and (pkt[1] == DISCONNECT or pkt[1] == CONNECT):
                        message = int(P2).to_bytes(1, 'big') + int(pkt[0]).to_bytes(1, 'big') + bytearray(PACKET_SIZE-3) + \
                            int(pkt[1]).to_bytes(1, 'big')
                        print("Len: ", len(message))
                        print("DC Message: ", message)
                        self.send_data(message)
                        continue

                    message = self.preprocess(pkt)
                    if message is not None:
                        print("Len msg: ", len(message))
                        for i in range(0, 10):
                            # send data in chunks of 48 -> 6*10*8 = 480
                            text = int(P2).to_bytes(
                                1, 'big') + pkt[0].to_bytes(
                                1, 'big') + message[i*(PACKET_SIZE-3):(i+1)*(PACKET_SIZE-3)] + int(CONNECT).to_bytes(1, 'big')
                            print("Message: ", text)
                            self.send_data(text)
                            time.sleep(0.2)
                        # check me (clear aft action)
                        time.sleep(2)
                        relay_buffer.queue.clear()
                elif(pkt[0] == VEST or pkt[0] == GUN) and len(pkt) == 2 and (pkt[1] == DISCONNECT or pkt[1] == CONNECT):
                    message = int(P2).to_bytes(1, 'big') + int(pkt[0]).to_bytes(1, 'big') + bytearray(PACKET_SIZE-3) + \
                        int(pkt[1]).to_bytes(1, 'big')
                    # print("Len: ", len(message))
                    print("DC Message: ", message)
                    self.send_data(message)
                elif pkt[0] == VEST and pkt[3] == SHOT_HIT:
                    message = int(P2).to_bytes(1, 'big') + pkt + bytearray(PACKET_SIZE-len(pkt)-2) + \
                        int(CONNECT).to_bytes(1, 'big')
                    print("Message: ", message)
                    print("Vest received shot hit")
                    self.send_data(message)

                    # wait for a while then clear pending data (debounce)
                    time.sleep(0.3)
                    relay_buffer.queue.clear()

                elif pkt[0] == GUN and pkt[3] == SHOT_FIRED:
                    message = int(P2).to_bytes(1, 'big') + pkt + bytearray(PACKET_SIZE-len(pkt)-2) + \
                        int(CONNECT).to_bytes(1, 'big')
                    print("Gun fired")
                    print("Message: ", message)
                    self.send_data(message)

                # else:
                    # print("Unknown packet: ", pkt)
            except (KeyboardInterrupt, ConnectionResetError, BrokenPipeError):
                print("Program stopped")
                has_closed = True
                self.conn.close()
                break

    def create_tunnel(self):
        try:
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
                ssh_address_or_host=(
                    'localhost', tunnel_sunfire.local_bind_port),
                # changed from remote
                remote_bind_address=('localhost', self.remote_port),
                ssh_username="xilinx",
                ssh_password=XILINX_PWD,
                local_bind_address=('localhost', self.local_port)
            )
            tunnel_xilinx.start()
            print(tunnel_xilinx.tunnel_is_up, flush=True)
            return tunnel_xilinx.local_bind_address
        except Exception as e:
            print("Reconnecting to tunnel")
            return self.create_tunnel()

    def send_data(self, message):
        rc = self.conn.sendall(bytes(message))
        if rc:
            print("Failed to send, with rc: ", rc)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('[Client] Invalid number of arguments')
        sys.exit()
    local_port = int(sys.argv[1])
    remote_port = int(sys.argv[2])
    group_id = sys.argv[3]
    conn_u96 = Client(local_port, remote_port, group_id)
    conn_u96.start()

    addr_list = [GLOVE_MAC, GUN_MAC, VEST_MAC]
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
