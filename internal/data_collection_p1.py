import time
import queue
import struct
from tracemalloc import start

from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from threading import Thread
from multiprocessing import Queue
import numpy as np
import csv
from statistics import median, mean, variance
from scipy.fftpack import fft
from scipy import stats

printed_data = []
SYN = 'S'
ACK = 'A'
NAK = 'N'

array_ax =[]
array_ay = []
array_az = []
array_gx =[]
array_gy = []
array_gz = []
array_axayaz_gxgygz =[]

#Need to send ACK and SYN as 20 byte packets as well

packetOne_len = 20

SOM_THRESHOLD = 0.8  # threshold value for start of move

counter = 0 #for timing purposes
fragmentedCounter = 0
droppedCounter = 0
partialpacket = False
firstData = False
startTime = 0
start = False
dataCounter = 0
cycle = False
actual_cycle = False
start_collection = False

Q = Queue()

class ScannerDelegate(DefaultDelegate):

    def __init__(self, char):
        DefaultDelegate.__init__(self)
        self.char = char
        self.done_handshake = False
        self.SeqID = 0

    def handleNotification(self,cHandle,data):

        if self.done_handshake: #and len(pkt) == packetOne_len: #when handshake is done
            full_packet = True
            pkt = bytearray(data)
            timer()

            #print("Packet: " + str(pkt)) #to see the packet

            if(len(pkt) == packetOne_len and pkt[0]==0):
                #print("Packet: " + str(pkt)) #to see the packet
                if pkt[2]==0:
                    correct_pkt = checksum(pkt)
                    self.SeqID = (self.SeqID + 1) & 0xFF

                    if(correct_pkt):
                        self.packetOne = bytearray(pkt[0:15])
                    else:
                        self.char.write(str.encode(NAK))
                        #print("Failed checksum")
                    
                elif pkt[2]==1:
                    full_packet = False
                    correct_pkt = checksum(pkt)
                    self.SeqID = (self.SeqID + 1) & 0xFF
                    if(correct_pkt):
                        self.packetTwo =bytearray(pkt[0:15])
                    else:
                        self.char.write(str.encode(NAK))
                        #print("Failed checksum")
                
                if(not full_packet and (self.packetOne[1] + 1 == self.packetTwo[1])):
                    Q.put(self.packetOne + self.packetTwo[3:15])

            elif(len(pkt) == packetOne_len and pkt[0]==1):
                print("IR detected")
                correct_pkt = checksum(pkt)
                self.SeqID = (self.SeqID + 1) & 0xFF
                if(correct_pkt):
                    self.char.write(str.encode(ACK))
                    Q.put(pkt)
                else:
                    self.char.write(str.encode(NAK))
                    
            elif(len(pkt) == packetOne_len and pkt[0]==2):
                print("Shot detected")
                correct_pkt = checksum(pkt)
                self.SeqID = (self.SeqID + 1) & 0xFF
                if(correct_pkt):
                    self.char.write(str.encode(ACK))
                    Q.put(pkt)
                else:
                    self.char.write(str.encode(NAK))


        elif data == str.encode(ACK): #Received ACK from bluno beetle after SYN is sent
            self.done_handshake = True
            self.char.write(str.encode(ACK))
        else:
            self.char.write(str.encode(SYN))

def timer():
    global startTime, counter, droppedCounter, fragmentedCounter, start, dataCounter,firstData,cycle
    
    if(time.time()-startTime >= 4): #and firstData):
        #print("Data Rate for " + addr + " is: " + str(counter/10000) + " KB/sec") #/1000 for KB and /10 to average in 10s
        #print("*******")
        cycle = True
        startTime = time.time()

def handshake(bluno, char, addr):
    done_handshake = False

    while done_handshake == False:
        if bluno.waitForNotifications(2.0): #establish connection
            done_handshake = True
            print("Handshake done")
        else:
            char.write(str.encode(SYN))
    
    print(addr + " completed handshake")
    return done_handshake

def extract_features(raw_data):
        extracted = []
        extracted = np.append(extracted, (np.min(raw_data)))
        extracted = np.append(extracted, (stats.iqr(raw_data)))
        extracted = np.append(extracted, (sum(raw_data)))
        extracted = np.append(extracted, (median(raw_data)))
        extracted = np.append(extracted, (variance(raw_data)))
        raw_data = fft(raw_data)
        extracted = np.append(extracted, np.min(abs(raw_data)))
        extracted = np.append(extracted, np.max(abs(raw_data)))
        extracted = np.append(extracted, mean(abs(raw_data)))
        extracted = np.append(extracted, stats.iqr(abs(raw_data)))
        extracted = np.append(extracted, variance(abs(raw_data)))
        return extracted

def display_data(queue):
    global cycle, actual_cycle, start_collection, array_ax,array_ay,array_az,array_gx,array_gy,array_gz, array_axayaz_gxgygz

    while True:
        try:
            pkt = queue.get()
            array_ax.append(struct.unpack("<f", pkt[15:19])[0])
            array_ay.append(struct.unpack("<f", pkt[19:23])[0])
            array_az.append(struct.unpack("<f", pkt[23:27])[0])
            array_gx.append(struct.unpack("<f", pkt[3:7])[0])
            array_gy.append(struct.unpack("<f", pkt[7:11])[0])
            array_gz.append(struct.unpack("<f", pkt[11:15])[0])
            ''' 
            print("%.5f" % struct.unpack("<f", pkt[15:19])[0], end = ' ') #ax: 
            print(", %.5f" % struct.unpack("<f", pkt[19:23])[0], end = ' ')#ay: 
            print(", %.5f" % struct.unpack("<f", pkt[23:27])[0], end = ' ')#az: 
            print(", %.5f" % struct.unpack("<f", pkt[3:7])[0], end = ' ') #little endian gx: 
            print(", %.5f" % struct.unpack("<f", pkt[7:11])[0], end = ' ') #gy: 
            print(", %.5f" % struct.unpack("<f", pkt[11:15])[0], end = ' ') #little endian gZ:
            '''
            print(len(array_ax))
            
            if (len(array_ax) >= 3 and start_collection == False):    
                print("Detecting start of move")
                if np.max(array_ax) + np.max(array_ay) + np.max(array_az) > SOM_THRESHOLD:
                    print("Start of move detected")
                    start_collection = True
                array_ax = []
                array_ay = []
                array_az = []
            '''
            if(pkt[0]==0 and start_collection and len(array_ax) < 40):
                if(actual_cycle):
                    print("")
                    print("%.5f" % struct.unpack("<f", pkt[15:19]), end = ' ') #ax: 
                    print(", %.5f" % struct.unpack("<f", pkt[19:23]), end = ' ')#ay: 
                    print(", %.5f" % struct.unpack("<f", pkt[23:27]), end = ' ')#az: 
                    print(", %.5f" % struct.unpack("<f", pkt[3:7]), end = ' ') #little endian gx: 
                    print(", %.5f" % struct.unpack("<f", pkt[7:11]), end = ' ') #gy: 
                    print(", %.5f" % struct.unpack("<f", pkt[11:15]), end = ' ') #little endian gZ:
                    actual_cycle = False
                    
                else:
                    print(", %.5f" % struct.unpack("<f", pkt[15:19]), end = ' ') #ax: 
                    print(", %.5f" % struct.unpack("<f", pkt[19:23]), end = ' ')#ay: 
                    print(", %.5f" % struct.unpack("<f", pkt[23:27]), end = ' ')#az: 
                    print(", %.5f" % struct.unpack("<f", pkt[3:7]), end = ' ') #little endian gx: 
                    print(", %.5f" % struct.unpack("<f", pkt[7:11]), end = ' ') #gy: 
                    print(", %.5f" % struct.unpack("<f", pkt[11:15]), end = ' ') #little endian gZ:
                if(cycle):
                    cycle = False
                    actual_cycle = True
            '''
            if len(array_ax) == 25 and start_collection:
                array_axayaz_gxgygz = []
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, extract_features(array_ax)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, extract_features(array_ay)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, extract_features(array_az)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, extract_features(array_gx)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, extract_features(array_gy)))
                array_axayaz_gxgygz = np.concatenate((
                    array_axayaz_gxgygz, extract_features(array_gz)))
                array_axayaz_gxgygz = np.float_(array_axayaz_gxgygz)
                array_ax = []
                array_ay = []
                array_az = []
                array_gx = []
                array_gy = []
                array_gz = []
                start_collection = False
                resp =input("Keep this data? (y/n) ")
                if(resp == 'y'): 
                    with open('hung_shield_p1.csv', 'a', encoding = 'UTF8', newline = '') as f:
                        writer = csv.writer(f)
                        writer.writerow(array_axayaz_gxgygz)
                
                array_ax = []
                array_ay = []
                array_az = []
                array_gx = []
                array_gy = []
                array_gz = []


        except KeyboardInterrupt:
            break


def connection(addr):
    is_connected = False

    service_uuid = "dfb0"
    char_id  = "dfb1"

    while is_connected == False:
        try:
            print("Establishing a connection with: " + addr)
            bluno = Peripheral(addr)
            
            #To turn on notifications
            service = bluno.getServiceByUUID( service_uuid )
            char = service.getCharacteristics( char_id )[0]

            bluno.setDelegate( ScannerDelegate(char))

            print("Bluno " + addr + " is connected")
            char.write( str.encode(SYN) )
            return bluno, char
        except Exception:
            print("Encounter an error when connecting..")
            pass


def connection_thread(bluno,char,addr):
    bluno_handshake = False
    global droppedCounter
    while True:
        try:
            #timer()
            if bluno_handshake:
                if bluno.waitForNotifications(1.5): #establish connection, wait for 2s
                    pass
                else:
                    # bluno.disconnect()
                    # print("Bluno " + addr + " has disconnected")
                    # bluno_handshake = False
                    # bluno,char = connection(addr)
                    # droppedCounter = droppedCounter + 1
                    pass
            else:
                bluno_handshake = handshake(bluno,char,addr)

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

    for digit in range(len(data) - 1): #same way calc on beetle
        checksum = (checksum ^ data[digit]) & 0xFF

    if checksum == data[len(data)-1]:
        counter = counter + len(data) - 3 #minue beetleID, seqID and checksum
        return True
    else:
        return False   


if __name__ == '__main__':
    
	addr_list = ["80:30:DC:D9:0C:C7"] 

	bluno_list = []
	char_list = []
	
	for addr in addr_list:
		bluno, char = connection(addr)
		bluno_list.append(bluno)
		char_list.append(char)
	
	for (b, c, a) in zip(bluno_list, char_list, addr_list): #zip creates [(bluno#, char#, addr#),..] for each bluno beetle
		t = Thread(target = connection_thread, args = (b, c, a, ))
		t.start()
	
	t_display_data = Thread(target = display_data, args = (Q,))
	t_display_data.start()
