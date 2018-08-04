//libraries for GPS
#include <SoftwareSerial.h>
#include <Adafruit_GPS.h>
// Connect the GPS Power pin to 5V
// Connect the GPS Ground pin to ground
// Connect the GPS TX (transmit) pin to Digital 3
// Connect the GPS RX (receive) pin to Digital 4

#define GPSECHO false //echo the gps readings to serial for debugging

/* declare the GPS object */
SoftwareSerial mySerial(3, 4);
Adafruit_GPS GPS(&mySerial);
bool GPSready = false;

boolean usingInterrupt = false; //used later
void useInterrupt(boolean); // Func prototype keeps Arduino 0023 happy

/*
 * =====================================================
 * API
 * =============================================
 */

bool initGPS(){
  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(9600);
//  turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  
  // the nice thing about this code is you can have a timer0 interrupt go off
  // every 1 millisecond, and read data from the GPS for you. that makes the
  // loop code a heck of a lot easier!
  useInterrupt(true);

//  wait 1 seconds. If we haven't received anything by then, something's wrong
  delay(1000);
  if (GPS.newNMEAreceived()){
    GPSready = true;
    return true;
  }
  else{
    return false;
  }
}

bool newGPSreading(){
  return ( GPSready && GPS.newNMEAreceived() );
}

bool fillReadingWithGPS(reading_t *reading){
  if (!GPSready || !newGPSreading() || !GPS.parse(GPS.lastNMEA()) ) { 
    reading->hasGPS = false;
    return false;  // we can fail to parse a sentence
  }
  reading->hasGPS = true;

  reading->year = GPS.year;
  reading->month = GPS.month;
  reading->day = GPS.day;
  reading->hour = GPS.hour;
  reading->minute = GPS.minute;
  reading->seconds = GPS.seconds;

  if (GPS.fix){
    reading->hasFix    = true;
    reading->latitude  = GPS.latitudeDegrees;
    reading->longitude = GPS.longitudeDegrees;
    reading->COG       = GPS.angle;
    reading->speed     = GPS.speed;
  }
  else{
    reading->hasFix    = false;
//    set to NaN
    reading->latitude  = sqrt(-1);
    reading->longitude = sqrt(-1);
    reading->COG       = sqrt(-1);
    reading->speed     = sqrt(-1);
  }
  return true;
}



/*
 * =================================================
 * interrupt stuff for reading from the GPS
 * =========================================================
 * We constantly have to tell the adafruit GPS library to ping the GPS and ask
 * if a new character is ready. Every time we call GPS.read(), the lib pings the GPS,
 * asking if it has a new char, and stores it if one's ready. 
 * Once a whole NMEA sentence is received then the GPS.newNMEAreceived() flag is set,
 * and we can actually parse the sentence in our main loop.
 * Basically all this fress us from calling GPS.read() in the main loop.
 */

SIGNAL(TIMER0_COMPA_vect) {
  char c = GPS.read();
  // if you want to debug, this is a good time to do it!
#ifdef UDR0
  if (GPSECHO)
    if (c) UDR0 = c;  
    // writing direct to UDR0 is much much faster than Serial.print 
    // but only one character can be written at a time. 
#endif
}

//Turn this feature on or off
void useInterrupt(boolean v) {
  if (v) {
    // Timer0 is already used for millis() - we'll just interrupt somewhere
    // in the middle and call the "Compare A" function above
    OCR0A = 0xAF;
    TIMSK0 |= _BV(OCIE0A);
    usingInterrupt = true;
  } else {
    // do not call the interrupt function COMPA anymore
    TIMSK0 &= ~_BV(OCIE0A);
    usingInterrupt = false;
  }
}
