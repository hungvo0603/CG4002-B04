// first part of https://www.dfrobot.com/blog-283.html, then use AT+MAC=? to get the MAC address
void setup()
{
    Serial.begin(115200); // initial the Serial
}

void loop()
{
    if (Serial.available())
    {
        Serial.write(Serial.read()); // send what has been received
    }
}
