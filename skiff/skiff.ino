/*
The arduino sketch run by the arduino on the skiff. 
Sends GPS and compass data to the big boat using the RFM69 radio chip.

The compass used is a "Adafruit LSM303DLHC" breakout board.

dependencies:
github.com/adafruit/Adafruit_GPS
github.com/adafruit/Adafruit_LSM303DLHC
LowPowerLab/RFM69

additionally, the GPS library requires
github.com/adafruit/Adafruit_Sensor
and the RFM69 library requires
github.com/LowPowerLab/SPIFlash
*/

//libraries for RFM69 radio chip
#include <SPIFlash.h>
#include <RFM69_ATC.h>
#include <RFM69_OTA.h>
#include <RFM69registers.h>

//libraries for GPS
#include <Adafruit_GPS.h>

//libraries for compass
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM303_U.h>
#include <Adafruit_LSM303.h>

void setup() {
  // put your setup code here, to run once:
  
}

void loop() {
  // put your main code here, to run repeatedly:

}


