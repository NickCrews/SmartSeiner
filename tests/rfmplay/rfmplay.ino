
//libraries for RFM69 radio chip
//#include <SPIFlash.h>
#include <SPI.h>                // Included with Arduino IDE
#include <RFM69.h>
#include <RFM69_ATC.h>
//#include <RFM69_OTA.h>

#include <SoftwareSerial.h>
SoftwareSerial mySerial(3, 4);

#define SERIAL_BAUD 115200

// Node and network config
#define NETWORK_ID     1  // The network ID
#define THIS_NODE_ID   2    // The ID of this node (must be different for every node on network)
#define OTHER_NODE_ID  1    
#define FREQUENCY     RF69_915MHZ // RF69_433MHZ //RF69_868MHZ // RF69_915MHZ
#define ENCRYPT_KEY         "abcdefghijklmnop" //has to be same 16 characters/bytes on all nodes!

// Uncomment if this board is the RFM69HW/HCW not the RFM69W/CW
//#define IS_RFM69HW_HCW

// Board and radio specific config - You should not need to edit
//#if defined (__AVR_ATmega32U4__) && defined (USING_RFM69_WING)
//    #define RF69_SPI_CS  10
//    #define RF69_RESET   11
//    #define RF69_IRQ_PIN 2
//    #define RF69_IRQ_NUM digitalPinToInterrupt(RF69_IRQ_PIN)
//#elif defined (__AVR_ATmega32U4__)
//    #define RF69_RESET    4
//    #define RF69_SPI_CS   8
//    #define RF69_IRQ_PIN  7
//    #define RF69_IRQ_NUM  4
//#elif defined(ARDUINO_SAMD_FEATHER_M0) && defined (USING_RFM69_WING)
//    #define RF69_RESET    11
//    #define RF69_SPI_CS   10
//    #define RF69_IRQ_PIN  6
//    #define RF69_IRQ_NUM  digitalPinToInterrupt(RF69_IRQ_PIN)
//#elif defined(ARDUINO_SAMD_FEATHER_M0)
//    #define RF69_RESET    4
//    #define RF69_SPI_CS   8
//    #define RF69_IRQ_PIN  3
//    #define RF69_IRQ_NUM  3
//#endif
#define RF69_RESET    4
#define RF69_SPI_CS   8 //we are redefining this. maybe ok?
#define RF69_IRQ_PIN  7 //we are redefining this. maybe ok?
#define RF69_IRQ_NUM  4

RFM69 radio(RF69_SPI_CS, RF69_IRQ_PIN, false, RF69_IRQ_NUM);
bool radioReady = false;

char spaceFiller[100];

void setup() {
  // put your setup code here, to run once:
    Serial.begin(SERIAL_BAUD);
    Serial.println("starting...");
//    delay(3000);
    if (initRadio()){
    Serial.println("Successfully loaded radio.");
    }
    else{
      Serial.println("Failed to initialize radio. Check wiring?");
    }
}

void loop() {
  // put your main code here, to run repeatedly:
  spaceFiller[7] = 'h';
  Serial.println("===================");
  radio.readAllRegs();
  Serial.print("temp: ");
  Serial.println(radio.readTemperature());
  Serial.println("===================");
  delay(1000);
  
}

bool initRadio(){
  bool success = radio.initialize(FREQUENCY,THIS_NODE_ID,NETWORK_ID);
  if (!success){
    return false;
  }
  
  #ifdef IS_RFM69HW_HCW
    radio.setHighPower(); //must include this only for RFM69HW/HCW!
  #endif
  
  radio.encrypt(ENCRYPT_KEY);

//  //Auto Transmission Control - dials down transmit power to save battery (-100 is the noise floor, -90 is still pretty good)
//  //For indoor nodes that are pretty static and at pretty stable temperatures (like a MotionMote) -90dBm is quite safe
//  //For more variable nodes that can expect to move or experience larger temp drifts a lower margin like -70 to -80 would probably be better
//  //Always test your ATC mote in the edge cases in your own environment to ensure ATC will perform as you expect
//  radio.enableAutoPower(ATC_RSSI);
  radioReady = true;
  return true;
}
