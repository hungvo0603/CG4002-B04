# Info:
# use p1 items

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

SYN = 'S'
ACK = 'A'
NAK = 'N'
DISCONNECT = 1
CONNECT = 0
GLOVE = 0
SOM_THRESHOLD = 0.8  # threshold value for start of move
PACKET_SIZE = 51  # player + type + 6 floats + disconnect
P1 = 0
P2 = 1
GUN_MAC = "D0:39:72:BF:C1:BF"
GLOVE_MAC = "C4:BE:84:20:1C:05"
VEST_MAC = "D0:39:72:BF:BF:ED"


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
            if(len(pkt) == packetOne_len and pkt[0] == GLOVE):
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
                    pass
            else:
                bluno_handshake = handshake(bluno, char, addr)
        except (KeyboardInterrupt, BrokenPipeError):
            has_closed = True
            bluno.disconnect()
            break
        except BTLEDisconnectError:
            if(addr == GLOVE_MAC and has_connected[addr]):
                has_connected[GLOVE_MAC] = False
                print("Glove disconnected")
                relay_buffer.put([GLOVE, DISCONNECT])
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
    def __init__(self):
        super().__init__()  # init parent (Thread)
        self.daemon = True
        self.start_collection = False
        self.array_ax = []
        self.array_ay = []
        self.array_az = []
        self.array_gx = []
        self.array_gy = []
        self.array_gz = []
        # need pynq?
        # self.input_buffer = [allocate(shape=(60,), dtype=np.float32), allocate(
        #     shape=(60,), dtype=np.float32)]

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
                    self.start_collection = True
                else:
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

    def pred_action(self, data, player):
        self.input_arr[player].extend(data)
        print("len of input arr: ", len(self.input_arr[player]))
        if len(self.input_arr[player]) < 60:
            return None

        actions = ["grenade", "shield", "reload", "nomovement"]

        for i in range(60):
            self.input_buffer[player][i] = float(self.input_arr[player][i])

        # print("Input buffer: ", self.input_buffer[player])
        print("Running prediction...")
        self.dma_send.sendchannel.transfer(self.input_buffer[player])
        self.dma_recv.recvchannel.transfer(self.output_buffer[player])
        self.dma_send.sendchannel.wait()
        self.dma_recv.recvchannel.wait()
        self.input_arr[player].clear()  # clear array after prediction
        print("len of input arr: ", len(self.input_arr[player]))
        # print("Cleared pipe after buffer")
        # clear(self.pred_relay)

        return actions[self.output_buffer[player][0]]

    def run(self):
        # Open tunnel and connect
        global has_closed
        while not has_closed:
            try:
                pkt = relay_buffer.get()
                if(pkt[0] == GLOVE):
                    if len(pkt) == 2 and pkt[1] == DISCONNECT:
                        print("[Client] Glove dc-ed")
                        continue

                    message = self.preprocess(pkt)
                    if message is not None:
                        print("Len msg: ", len(message))
                        print("Message: ", message)

                        # can do prediction here directly
                        # self.pred_action(message, P1)

                        for i in range(0, 10):
                            # send data in chunks of 48 -> 6*10*8 = 480
                            text = int(P1).to_bytes(
                                1, 'big') + pkt[0].to_bytes(
                                1, 'big') + message[i*(PACKET_SIZE-3):(i+1)*(PACKET_SIZE-3)] + int(CONNECT).to_bytes(1, 'big')
                            print("Message: ", text)
                            # send to ml model
                            self.send_data(text)
                            time.sleep(0.2)
                        # check me (clear aft action)
                        time.sleep(5)
                        relay_buffer.queue.clear()
                else:
                    print("Unknown packet: ", pkt)

            except (KeyboardInterrupt, ConnectionResetError, BrokenPipeError):
                print("Program stopped")
                has_closed = True
                self.conn.close()
                break


if __name__ == '__main__':
    conn_u96 = Client()
    conn_u96.start()

    addr_list = [GLOVE_MAC]  # , GUN_MAC, VEST_MAC
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
