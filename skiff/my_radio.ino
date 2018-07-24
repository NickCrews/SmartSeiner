
//libraries for RFM69 radio chip
#include <SPIFlash.h>
#include <SPI.h>                // Included with Arduino IDE
#include <RFM69.h>
#include <RFM69_ATC.h>
//#include <RFM69_OTA.h>

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

void echoRadio(){
  if (radio.receiveDone()) // Got one!
  {
    // Print out the information:
    
    Serial.print("received from node ");
    Serial.print(radio.SENDERID, DEC);
    Serial.print(": [");

    // The actual message is contained in the DATA array,
    // and is DATALEN bytes in size:
    
    for (byte i = 0; i < radio.DATALEN; i++)
      Serial.print((char)radio.DATA[i]);

    // RSSI is the "Receive Signal Strength Indicator",
    // smaller numbers mean higher power.
    
    Serial.print("], RSSI ");
    Serial.println(radio.RSSI);

    // Send an ACK if requested.
    // (You don't need this code if you're not using ACKs.)
    
    if (radio.ACKRequested())
    {
      radio.sendACK();
      Serial.println("ACK sent");
    }
  }
}
bool radioSend(char* msg){
  int numRetries = 1;
  return radio.sendWithRetry(OTHER_NODE_ID, msg, strlen(msg), numRetries);
}
//
//// Reset the Radio
//void resetRadio() {
//    if (Serial) Serial.print("Resetting radio...");
//    pinMode(RF69_RESET, OUTPUT);
//    digitalWrite(RF69_RESET, HIGH);
//    delay(20);
//    digitalWrite(RF69_RESET, LOW);
//    delay(500);
//}
