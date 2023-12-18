#include "SerialTransfer.h"
#include "DHT.h"
#define DHTTYPE DHT11

const long dry = 590; // value for dry sensor
const long wet = 280; // value for wet sensor

SerialTransfer myTransfer;

DHT dht(2, DHTTYPE);
DHT dht2(3, DHTTYPE);

struct __attribute__((packed)) STRUCT {
  long soilMoisture; //soil moisture of the plant bed 
  long temp; //inside temperature of the growth container
  long humidity; //inside humidity of the growth container 
  long envTemp; //outside temperature of the ambient environment
  long envHumidity; //outside humidity of the ambient environment
} data;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  myTransfer.begin(Serial);
  dht.begin();
  dht2.begin();
}

void loop() {
  // put your main code here, to run repeatedly:
  data.soilMoisture = map(analogRead(A0), wet, dry, 100, 0);
  data.temp = dht.readTemperature();
  data.humidity = dht.readHumidity();
  data.envTemp = dht2.readTemperature();
  data.envHumidity = dht2.readHumidity();

  //send data array 
  uint16_t sendSize = 0;
  sendSize = myTransfer.txObj(data, sendSize);
  myTransfer.sendData(sendSize);
  
  delay(1000);
}
