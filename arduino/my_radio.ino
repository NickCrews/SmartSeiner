
//libraries for RFM69 radio chip
#include <RFM69.h>
//#include <RFM69_ATC.h>
//#include <RFM69_OTA.h>

// Node and network config
#define NETWORK_ID     1  // The network ID
#define THIS_NODE_ID   2    // The ID of this node (must be different for every node on network)
#define OTHER_NODE_ID  1
#define FREQUENCY     RF69_915MHZ // RF69_433MHZ //RF69_868MHZ // RF69_915MHZ

RFM69 radio;
bool radioReady = false;

bool initRadio(){
  bool success = radio.initialize(FREQUENCY,THIS_NODE_ID,NETWORK_ID);
  if (!success){
    return false;
  }

  radio.setHighPower(); //NEED THIS since using HCW version of RFM69

  // set bitrate to 1.2 kbps from library default of 55kbps
  // This decreases the receivers sensivity to noise, increasing range
  radio.writeReg(0x03, 0x68);
  radio.writeReg(0x04, 0x2B);

//  //Auto Transmission Control - dials down transmit power to save battery (-100 is the noise floor, -90 is still pretty good)
//  //For indoor nodes that are pretty static and at pretty stable temperatures (like a MotionMote) -90dBm is quite safe
//  //For more variable nodes that can expect to move or experience larger temp drifts a lower margin like -70 to -80 would probably be better
//  //Always test your ATC mote in the edge cases in your own environment to ensure ATC will perform as you expect
//  radio.enableAutoPower(ATC_RSSI);
  radioReady = true;
  return true;
}

// void echoRadio(){
//   if (radio.receiveDone()) // Got one!
//   {
//     // Print out the information:
//
//     Serial.print("received from node ");
//     Serial.print(radio.SENDERID, DEC);
//     Serial.print(": [");
//
//     // The actual message is contained in the DATA array,
//     // and is DATALEN bytes in size:
//
//     for (byte i = 0; i < radio.DATALEN; i++)
//       Serial.print((char)radio.DATA[i]);
//
//     // RSSI is the "Receive Signal Strength Indicator",
//     // smaller numbers mean higher power.
//
//     Serial.print("], RSSI ");
//     Serial.println(radio.RSSI);
//
//     // Send an ACK if requested.
//     // (You don't need this code if you're not using ACKs.)
//
//     if (radio.ACKRequested())
//     {
//       radio.sendACK();
//       Serial.println("ACK sent");
//     }
//   }
// }

void radioSend(void* msg, uint8_t len){
  bool requestAck = false;
  radio.send(OTHER_NODE_ID, msg, len, requestAck);
}
