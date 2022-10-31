#include "GY521.h"
#include "Arduino.h"

GY521 sensor(0x68); //ADU to GND
uint32_t counter = 0;

float ax, ay, az;
float gx, gy, gz;

#define SYN 'S'
#define ACK 'A'
#define NAK 'N'

byte packetOne[20];
byte packetTwo[20];

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
long packetSegments = 2;
byte SeqID = 0x00;
byte BeetleID = 0x00;

int ledIndicator = A2; // led lights up every 2 second
const char kDelimiter = ',';    
const int kSerialInterval = 50; // Interval between readings
unsigned long serialPreviousTime; 



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

typedef union { //define a type with the following attributes
  //union allows to store different data types in the same memory location
  //only one member can contain a value at any given time, so when a value is assigned to Data, byteData will parse the value according to the index
  float Data; //float is 4 bytes
  byte byteData[4]; //max of 4 bytes
} byteConversion;

int packagingData (int index, byte pkt[], float value){
  byteConversion fullData;//declare a variable of type convertedData
  fullData.Data = value;//assign the attribute with the value

  for(int i=0;i<4;i++){
    pkt[index] = fullData.byteData[i]; //Add one byte of data to the packet at each index incrementally
    index++;
  }
  return index;
}

void addDataToPacket(byte pkt[], float D1, float D2, float D3){
  int index = 3; //start with index 3, since index 0 is the SeqID and index 1 is BeetleID
  index = packagingData(index,pkt,D1); //function will return index = 5 and will add the data to the packet
  index = packagingData(index,pkt,D2); //starting index = 5 and will add data to the packet 
  index = packagingData(index,pkt,D3);
}


void setup()
{
  while (!Serial && (millis() < 10000));
  Serial.begin(115200);
  Wire.begin();
  pinMode (ledIndicator, OUTPUT);
  delay(100);
  
  while (sensor.wakeup() == false)
  {
    Serial.write(millis());
    Serial.write("\tCould not connect to GY521 0x69\n");
    delay(1000);
  }

  sensor.setAccelSensitivity(2);  // 8g
  sensor.setGyroSensitivity(1);   // 500 degrees/s
  sensor.setThrottle();

  // set all calibration errors to zero
  sensor.axe = 0;
  sensor.aye = 0;
  sensor.aze = 0;
  sensor.gxe = 0;
  sensor.gye = 0;
  sensor.gze = 0;

  delay(2000);

  ax = ay = az = 0;
  gx = gy = gz = 0;
  
  for (int i = 0; i < 20; i++)
  {
    sensor.read();
    ax += sensor.getAccelX();
    ay += sensor.getAccelY();
    az += sensor.getAccelZ();
    gx += sensor.getGyroX();
    gy += sensor.getGyroY();
    gz += sensor.getGyroZ();
  }

  ax /= 20;
  ay /= 20;
  az /= 20;
  gx /= 20;
  gy /= 20;
  gz /= 20;

  sensor.axe = ax;
  sensor.aye = ay;
  sensor.aze = az;
  sensor.gxe = gx;
  sensor.gye = gy;
  sensor.gze = gz;
  delay(100);
}


void loop() {

  if((millis() - serialPreviousTime) > kSerialInterval) 
  {
    
    serialPreviousTime = millis(); //update time

    ax = ay = az = 0;
    gx = gy = gz = 0;
    
    for (int i = 0; i < 20; i++)
    {
      sensor.read();
      ax -= sensor.getAccelX();
      ay -= sensor.getAccelY();
      az -= sensor.getAccelZ();
      gx -= sensor.getGyroX();
      gy -= sensor.getGyroY();
      gz -= sensor.getGyroZ();
    }
  
    if(doneHandshake){

      digitalWrite(ledIndicator, HIGH); 
      
      //read and send data, if waiting ACK, will skip this part
        packetOne[0] = BeetleID;
        packetOne[1] = SeqID;
        packetOne[2] = 0x00;
        addDataToPacket(packetOne, 
        (ax * 2.5 > 100 ? 1 : (ax * 2.5 < -100 ? -1 : ax / 40)),
        (ay * 2.5 > 100 ? 1 : (ay * 2.5 < -100 ? -1 : ay / 40)),
        (az * 2.5 > 100 ? 1 : (az * 2.5 < -100 ? -1 : az / 40)));
        addChecksumToPacket(packetOne, packetsize);
        
          Serial.write(packetOne,packetsize); 
        
        SeqID++;
  
        packetTwo[0] = BeetleID;
        packetTwo[1] = SeqID;
        packetTwo[2] = 0x01;
        addDataToPacket(packetTwo,
        gx * 0.05 > 200 ? 1 : (gx * 0.05 < -200 ? -1 : gx / 4000),
        gy * 0.05 > 200 ? 1 : (gy * 0.05 < -200 ? -1 : gy / 4000),
        gz * 0.05 > 200 ? 1 : (gz * 0.05 < -200 ? -1 : gz / 4000));
        addChecksumToPacket(packetTwo, packetsize);

        //while(!Serial.available()){}
        Serial.write(packetTwo,packetsize);
  
        SeqID++;
  
        delay(50);
  
        char response = packetACK();
  
    }

  else { //if handshake not done
    if(rcvSYN){
      if(handshake()){
        doneHandshake = true;
        delay(5000);
      }
    }
    else{
      rcvSYN = waitForSYN;
      delay(500);
    }
  }
    
    sensor.axe += ax * 0.05;
    sensor.aye += ay * 0.05;
    sensor.aze += az * 0.05;
    sensor.gxe += gx * 0.05;
    sensor.gye += gy * 0.05;
    sensor.gze += gz * 0.05;    
  }
}
