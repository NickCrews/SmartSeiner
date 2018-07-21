/*
The arduino sketch run by the arduino on the skiff.
Sends GPS and compass data to the big boat using the RFM69 radio chip.

Some code taken from http://rpi-rfm69.readthedocs.io/en/latest/example_arduino.html

dependencies:
github.com/adafruit/Adafruit_GPS
github.com/adafruit/Adafruit_LSM303DLHC
LowPowerLab/RFM69

additionally, the GPS library requires
github.com/adafruit/Adafruit_Sensor
and the RFM69 library requires
github.com/LowPowerLab/SPIFlash
*/

#define SERIAL_BAUD   115200

typedef struct {
  float         x;
  float         y;
  float         z;
} vec3_t;

typedef struct {
  bool hasGPS, hasMagAcc;
  uint8_t hour, minute, seconds, year, month, day;
  bool hasFix;
  float         latitude;
  float         longitude;
  vec3_t acceleration, magnetic;
} reading_t;

void setup(){
  Serial.begin(SERIAL_BAUD);
  Serial.println("starting...");
  
  if (initMagAccSensor()){
    Serial.println("Successfully loaded magnetometer/accelerometer.");
  }
  else{
    Serial.println("Failed to initialize magnetometer/accelerometer. Check wiring?");
  }

  if (initGPS()){
    Serial.println("Successfully loaded GPS.");
  }
  else{
    Serial.println("Failed to initialize GPS. Check wiring?");
  }

  if (initRadio()){
    Serial.println("Successfully loaded radio.");
  }
  else{
    Serial.println("Failed to initialize radio. Check wiring?");
  }
}

void loop(){
  delay(100);
//  if (!newGPSreading()) return;
  
  reading_t reading;
//  fillReadingWithGPS(&reading);
  fillReadingWithMagAcc(&reading);
  printReading(&reading);
  float x = reading.acceleration.x;
  float y = reading.acceleration.y;
  float z = reading.acceleration.z;
  Serial.println(pitch(x,y,z));
  Serial.println(roll(x,y,z));
}

float pitch(float accX, float accY, float accZ){
  return atan2(-accX, sqrt(accY*accY + accZ*accZ)) * 180/M_PI;
}

float roll(float accX, float accY, float accZ){ 
//  miu correction from https://stackoverflow.com/a/30195572/5156887
  int sign  = accZ>0 ? 1 : -1 ;
  float miu = 0.001;
  float roll_rad  = atan2( accY,   sign* sqrt(accZ*accZ+ miu*accX*accX));
  return roll_rad * 180/M_PI;
}




void formatReading(String* result, reading_t *reading){
  *result = "{";

  *result += "\"hasGPS\":";
  *result += String(reading->hasGPS);

  if (reading->hasGPS){
    *result += ", \"date\":\"";
  //  Serial.println(result);
    *result += String(reading->month);
    *result += "/";
    *result += String(reading->day);
    *result += "/";
    *result += String(reading->year);
  
    *result += "\", \"time\":\"";
    *result += String(reading->hour);
    *result += ":";
    *result += String(reading->minute);
    *result += ":";
    *result += String(reading->seconds);
    *result += "\"";

    *result += ", \"hasFix\":";
    *result += String(reading->hasFix);
    if (reading->hasFix){
      *result += ", \"lat\":";
      *result += String(reading->latitude, 6);

      *result += ", \"lon\":";
      *result += String(reading->longitude, 6);;
    }
  }

  *result += ", \"hasMagAcc\":";
  *result += String(reading->hasMagAcc);

  if (reading->hasMagAcc){
    *result += ", \"acc\":[";
    *result += String(reading->acceleration.x, 4);
    *result += ", ";
    *result += String(reading->acceleration.y, 4);
    *result += ", ";
    *result += String(reading->acceleration.z, 4);
    *result += "]";
    
    *result += ", \"mag\":[";
    *result += String(reading->magnetic.x, 4);
    *result += ", ";
    *result += String(reading->magnetic.y, 4);
    *result += ", ";
    *result += String(reading->magnetic.z, 4);
    *result += "]";
  }
  *result += "}";
}
void printReading(reading_t *reading){
  String resultString;
  formatReading(&resultString, reading);
  Serial.println(resultString);
}

void Blink(byte PIN, byte DELAY_MS)
{
  pinMode(PIN, OUTPUT);
  digitalWrite(PIN,HIGH);
  delay(DELAY_MS/2);
  digitalWrite(PIN,LOW);
  delay(DELAY_MS/2);
}
