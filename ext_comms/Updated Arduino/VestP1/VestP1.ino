#include <Arduino.h>
#include <IRremote.hpp>
#define IR_RECEIVE_PIN         2 
#define LED_INDICATOR          4

#include "GY521.h"
#include <Arduino.h>
#include <IRremote.hpp>
#define IR_RECEIVE_PIN         2 
#define LED_INDICATOR          4

#define SYN 'S'
#define ACK 'A'
#define NAK 'N'

byte packet[20];

int packetsize = 20;

long startTime = 0;
long sendTime;
long timeout = 1000; //timeout of 1 second


bool doneHandshake = false;
bool rcvSYN = false;

bool readData = false;
bool sendData = false;
bool packetDone = false;
bool IR_Hit = false;
bool check = false;

long retransmitCount = 0;
byte SeqID = 0x00;
byte BeetleID = 0x01;//vest
int data = 0x00; //107 in decimal


bool waitForSYN(){ //SYN from laptop
  bool SYN_detected = false;

  if(Serial.available()){
    char response = Serial.read(); //take note char is 1 byte, waiting for SYN
    if(response == SYN){
      Serial.write(ACK);
      SYN_detected = true;
    }
  }
  
  return SYN_detected;
}


bool waitForACK(){ //SYN from laptop
  bool ACK_detected = false;

  if(Serial.available()){
    char response = Serial.read(); //take note char is 1 byte, waiting for SYN
    if(response == ACK){
      ACK_detected = true;
    }
  }
  return ACK_detected;
}

bool handshake(){ //wait for ACK from laptop to establish 3 way handshake
  bool isHandshake = false;
  Serial.write(ACK);

  while(Serial.available()&&isHandshake==false){
    char response = Serial.read();
    if(response == ACK){
      Serial.flush(); //might not need
      isHandshake = true;
    }
    delay(50);
  }
  return isHandshake;
}

char packetACK (){ //Waiting for ACK/NAK after sending packet
  if(Serial.available()){
    char response = Serial.read();

    if(response == ACK){
      return ACK;
    }
    else if (response == NAK){
      return NAK;
    }
    else{
      return 'W'; //means waiting
    }
    
  }
}

byte calculateChecksum(byte pkt[], int pktsize){
  byte checksum = 0;

  for(int digit=0;digit<pktsize-1;digit++){
    checksum ^=pkt[digit]; //xor checksum used, to be calc the same way at laptop to detect bit errors
  }
  return checksum;
}

void addSeqIDToPacket(byte pkt[], char SeqID){ //not used
  int index = 1; //second bit of packet
  pkt[index] = (byte) SeqID;
}

void addBeetleIDToPacket(byte pkt[], char BeetleID){
  int index = 0; //first bit of packet
  pkt[index] = (byte) BeetleID;
}

void addChecksumToPacket(byte pkt[], int pktsize){
  int index = pktsize - 1; //last bit of packet
  pkt[index] = calculateChecksum(pkt, pktsize);
}


void addDataToPacket(byte pkt[], int data){
  int index = 3; //start with index 3, since index 0 is the SeqID and index 1 is BeetleID
  pkt[index] = (byte) data;
}

void setup() {
    while (!Serial && (millis() < 10000));
    Serial.begin(115200);
    IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
    pinMode(LED_INDICATOR, OUTPUT); 
}

void loop() {
    if(doneHandshake){
      if(Serial.read() == SYN){
        doneHandshake = false;
        digitalWrite(LED_INDICATOR, HIGH);
        delay(7000);
      }
      if (IrReceiver.decode()){
        IrReceiver.resume();
        if (IrReceiver.decodedIRData.address == 0x7812 && IrReceiver.decodedIRData.command == 0x28) {
            digitalWrite(LED_INDICATOR, HIGH);
            data = 0xA1;
            //Serial.print("Data Received");
        } else {
            data = 0xA0;
        }  
      packet[0] = BeetleID;
      packet[1] = SeqID;
      packet[2] = (byte) 0x00;
      addDataToPacket(packet,data);
      addChecksumToPacket(packet, packetsize);
      delay(1000);
      Serial.write(packet,packetsize);
      delay(500);
      SeqID++;
      } else {
        digitalWrite(LED_INDICATOR, LOW);
      }
    } 
    else { //if handshake not done
    if(rcvSYN){
      digitalWrite(LED_INDICATOR, HIGH);
      if(handshake()){
        doneHandshake = true;
        delay(1000);
      }
    }
    else{
      rcvSYN = waitForSYN();
      delay(500);
    }
  }
}
