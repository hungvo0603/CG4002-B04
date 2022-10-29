import time
import queue
import struct
from tracemalloc import start

from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from threading import Thread
from multiprocessing import Queue

printed_data = []
SYN = 'S'
ACK = 'A'
NAK = 'N'

#Need to send ACK and SYN as 20 byte packets as well

packetOne_len = 20

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


def display_data(queue):
    global firstData, startTime, dataCounter,cycle, actual_cycle

    while True:
        try:
            pkt = queue.get()

            if(pkt[0]==0):
                #print("Packet: " + str(pkt)) to see the packet
                #print("Beetle ID: " + str(pkt[0]))
                #print("Sequence ID: " + str(pkt[1]))
                #print("IMU Data")
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

            elif(pkt[0]==1 and str(pkt[3])=='6278'):
                print("IR Hit Detectation verified")
                #print("Sequence ID: " + str(pkt[1]))
                #print("Data received from Bluno Beetle: " + str(pkt[3]))
            elif(pkt[0]==2 and str(pkt[3])=='188'):
                print("Shot Detection verified")                         

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
    
	addr_list = ["C4:BE:84:20:1C:05"] 

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
