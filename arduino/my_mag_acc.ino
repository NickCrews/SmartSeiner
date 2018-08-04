//libraries for compass and accelerometer
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM303_U.h>
//GND->GND
//VIN->5v (It will also work on 3.3v)
//SDA->SDA (A4 on 'classic' Arduinos)
//SCL->SCL (A5 on 'classic' Arduinos)

// how many degrees E of true north is the magnetic north pole in this area?
#define DECLINATION 0.0

/* Assign a unique ID to this sensor at the same time */
Adafruit_LSM303_Mag_Unified mag = Adafruit_LSM303_Mag_Unified(12345);
Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(54321);

bool magAccReady = false;
/*
 * ============================================================
 * API
 * ============================================================
 */

bool initMagAccSensor(){
  /* Initialise the sensor. Return if successful */
  mag.enableAutoRange(true);
  if (mag.begin() && accel.begin()){
    magAccReady = true;
    return true;
  }
  else{
    return false;
  }
}

bool fillReadingWithMagAcc(reading_t *reading){
  if (!magAccReady){
    reading->hasMagAcc = false;
    return false;
  }
  reading->hasMagAcc = true;
  sensors_event_t event;

  accel.begin();
  accel.getEvent(&event);
  reading->acceleration.x = event.acceleration.x;
  reading->acceleration.y = event.acceleration.y;
  reading->acceleration.z = event.acceleration.z;

  mag.begin();
  mag.enableAutoRange(true);
  mag.getEvent(&event);
  reading->magnetic.x = event.magnetic.x;
  reading->magnetic.y = event.magnetic.y;
  reading->magnetic.z = event.magnetic.z;
  return true;
}

float getBearing(){
  sensors_event_t event;
  mag.getEvent(&event);
  
  float Pi = 3.14159;
  // Calculate the angle of the vector y,x
  float heading = (atan2(event.magnetic.y, event.magnetic.x) * 180) / Pi;
//  convert from magnetic to geographic north
  heading = heading + DECLINATION;
  // Normalize to 0-360
  if (heading < 0)
  {
    heading = 360 + heading;
  }

  return heading;
}



