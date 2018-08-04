
import numpy as np
import atexit

from RFM69 import Radio, FREQ_915MHZ
import datetime
import time

THIS_NODE_ID = 2
NETWORK_ID = 1
OTHER_NODE_ID = 2

# with Radio(FREQ_915MHZ, THIS_NODE_ID, NETWORK_ID, isHighPower=True, verbose=True) as radio:
#     print ("Starting loop...")
#
#     rx_counter = 0
#     tx_counter = 0
#
#     while True:
#
#         # Every 10 seconds get packets
#         if rx_counter > 10:
#             rx_counter = 0
#
#             # Process packets
#             for packet in radio.get_packets():
#                 print (packet)
#
#         # Every 5 seconds send a message
#         if tx_counter > 5:
#             tx_counter=0
#
#             # Send
#             print ("Sending")
#             if radio.send(2, "TEST", attempts=3, waitTime=100):
#                 print ("Acknowledgement received")
#             else:
#                 print ("No Acknowledgement")
#
#
#         print("Listening...", len(radio.packets), radio.mode_name)
#         delay = 0.5
#         rx_counter += delay
#         tx_counter += delay
#         time.sleep(delay)

import compass

class Skiff(object):

    def __init__(self, compass_file=None):
        self.compass = compass.Compass()
        atexit.register(self._cleanup)
        # self.radio = Radio(FREQ_915MHZ,
        #                    THIS_NODE_ID,
        #                    NETWORK_ID,
        #                    isHighPower=True,
        #                    verbose=False)
        self.has_new_data = False

    def get_data(self):
        # self._update()
        data = {}
        data['lat']        = np.nan
        data['lon']        = np.nan
        data['datetime']   = np.nan
        data['COG']        = np.nan
        data['heading']    = np.nan
        data['speed']      = np.nan
        self.has_new_data = False
        return data

    def _cleanup(self):
        if hasattr(self, "radio") and self.radio:
            self.radio._shutdown()
