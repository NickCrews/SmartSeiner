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
*/
#include <avr/wdt.h> //watchdog timer
#define SERIAL_BAUD   115200

#define NUM_BYTES_SENT 16
float NaN = sqrt(-1);

typedef struct {
  float         x;
  float         y;
  float         z;
} vec3_t;

typedef struct {
  bool hasGPS, hasMagAcc;
  uint8_t hour, minute, seconds, year, month, day;
  bool hasFix;
  float latitude;
  float longitude;
  float COG; //Course Over Ground, ie direction of travel
  // Not to be confused with heading, the direction the skiff is pointed.
  float speed;
  vec3_t acceleration, magnetic;
} reading_t;

reading_t reading;
byte packed_bytes[NUM_BYTES_SENT];

void setup(){
//  Enable the watchdog timer to timeout after 8 sec.
//  If we don't get a call to wdt_reset() every 8 sec, reboot the arduino.
//  This is a savage way with the pesky freezeups I can't track down
  wdt_enable(WDTO_8S);
  Serial.begin(SERIAL_BAUD);
  Serial.println("Starting...");
  initReading(&reading);
  
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
  Serial.println("Starting loop...");
  Serial.flush();
}

void loop(){
  delay(100);
  wdt_reset(); //reset the watchdog timer

  Serial.println("filling!");
  fillReadingWithGPS(&reading);
  Serial.print(reading.hour);
  Serial.print(":");
  Serial.print(reading.minute);
  Serial.print(":");
  Serial.println(reading.seconds);
  
//  fillReadingWithMagAcc(&reading);
//  printReading(&reading);
//  float x = reading.acceleration.x;
//  float y = reading.acceleration.y;
//  float z = reading.acceleration.z;
//  Serial.println(pitch(x,y,z));
//  Serial.println(roll(x,y,z));

  Serial.println("packing!");
  reading2bytes(packed_bytes, &reading);
  Serial.println("sending!");
  radioSend(packed_bytes, NUM_BYTES_SENT);
}

//float pitch(float accX, float accY, float accZ){
//  return atan2(-accX, sqrt(accY*accY + accZ*accZ)) * 180/M_PI;
//}
//
//float roll(float accX, float accY, float accZ){
////  miu correction from https://stackoverflow.com/a/30195572/5156887
//  int sign  = accZ>0 ? 1 : -1 ;
//  float miu = 0.001;
//  float roll_rad  = atan2( accY,   sign* sqrt(accZ*accZ+ miu*accX*accX));
//  return roll_rad * 180/M_PI;
//}

void reading2bytes(byte result[NUM_BYTES_SENT], reading_t* reading){
  /*  Populate an array of bytes with the values stored in a reading.
   *  This array of bytes will then be sent over the radio and unpacked 
   *  by the Raspberry Pi.
   */

//  bytes 0-3 contain the latitude
  byte pos = 0;
  byte* b = (byte *) &(reading->latitude);
  for (int i=0; i<4; i++){
    result[pos+i] = b[i];
  }

//  bytes 4-7 contain the longitude
  pos = pos + 4;
  b = (byte *) &(reading->longitude);;
  for (int i=0; i<4; i++){
    result[pos+i] = b[i];
  }

//  bytes 8-11 contain the Course Over Ground
  pos = pos + 4;
  b = (byte *) &(reading->COG);;
  for (int i=0; i<4; i++){
    result[pos+i] = b[i];
  }

//  bytes 12-15 contain the speed
  pos = pos + 4;
  b = (byte *) &(reading->speed);;
  for (int i=0; i<4; i++){
    result[pos+i] = b[i];
  }
}

void formatReading(String* result, reading_t* reading){
  /* Turn a reading into a json string. Not currently used.*/
  *result = "{";

  *result += "\"hasGPS\":";
  *result += String(reading->hasGPS);

  if (reading->hasGPS){
    *result += ", \"date\":\"";
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

void initReading(reading_t *reading){
  reading->hasGPS    = false;
  reading->hasMagAcc = false;
  reading->hasFix    = false;
  reading->hour      = 255;
  reading->minute    = 255;
  reading->seconds   = 255;
  reading->year      = 255;
  reading->month     = 255;
  reading->day       = 255;
  
  reading->latitude  = NaN;
  reading->longitude = NaN;
  reading->COG       = NaN;
  reading->speed     = NaN;
  
  reading->acceleration.x = NaN;
  reading->acceleration.y = NaN;
  reading->acceleration.z = NaN;
  
  reading->magnetic.x = NaN;
  reading->magnetic.y = NaN;
  reading->magnetic.z = NaN;
}

