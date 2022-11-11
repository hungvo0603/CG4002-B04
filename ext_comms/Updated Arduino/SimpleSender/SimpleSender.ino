#include <ezButton.h>
#include <Arduino.h>
#include <IRremote.hpp>
#include <Arduino.h>
#include <IRremote.hpp>

ezButton button(2);
#define IR_SEND_PIN         4 //ir emitter
#define SYN 'S'
#define ACK 'A'
#define NAK 'N'
#define BUZZER_PIN          A2

uint16_t click_counter = 0; //6 bullets in game

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

long retransmitCount = 0;
byte SeqID = 0x00;
byte BeetleID = 0x02; //gun
int data = 0xB6; //188

uint16_t sAddress = 0x7820;
uint8_t sCommand = 0x72;
uint8_t sRepeats = 0;


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
      //Serial.write(ACK);
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
    button.setDebounceTime(50);
    IrSender.begin(IR_SEND_PIN); // Start with IR_SEND_PIN as send pin and if NO_LED_FEEDBACK_CODE is NOT defined, enable feedback LED at default feedback LED pin
    pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {

  button.loop();

  if(doneHandshake){
      if(button.isPressed()){
      //Serial.println("Button is pressed");
      IrSender.sendNEC(sAddress, sCommand, sRepeats);
      digitalWrite(BUZZER_PIN, HIGH);
      packet[0] = BeetleID;
      packet[1] = SeqID;
      packet[2] = (byte) 0x00;
      addDataToPacket(packet,data);
      addChecksumToPacket(packet, packetsize);
      Serial.write(packet,packetsize);
      delay(100);
      SeqID++;
    }
    if(button.isReleased()){
      //Serial.println("Button is released");
      digitalWrite(BUZZER_PIN, LOW); 
    }
  } 
  else {
    if(rcvSYN){
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
