import logging
logger = logging.getLogger(__name__)

import numpy as np
import time
from struct import unpack
from threading import Thread
from queue import Queue

from RFM69 import Radio, FREQ_915MHZ

import compass

NETWORK_ID = 1
THIS_NODE_ID = 1
OTHER_NODE_ID = 2

class Skiff(object):

    def __init__(self, compass_file=None):
        self.compass = compass.Compass()
        self.has_new_data = False
        self.radio = MyRadio()

    def has_data(self):
        return self.radio.has_data()

    def get_data(self):
        all_readings = self.radio.get_data()
        # print("allreading:", all_readings)
        if len(all_readings) < 1:
            return dict(lat=np.nan,
                        lon=np.nan,
                        COG=np.nan,
                        speed=np.nan
                        )
        most_recent_bytes = all_readings[-1]
        dictionary = self.parse_bytes(most_recent_bytes)
        self.has_new_data = False
        return dictionary

    def parse_bytes(self, byte_list):
        assert len(byte_list) == 16
        lat   = self.bytes2float(byte_list[0:4])
        lon   = self.bytes2float(byte_list[4:8])
        COG   = self.bytes2float(byte_list[8:12])
        speed = self.bytes2float(byte_list[12:16])
        return dict(lat=lat,
                    lon=lon,
                    COG=COG,
                    speed=speed)

    def bytes2float(self, byte_list):
        assert len(byte_list) == 4
        byte_array = bytearray(byte_list)
        python_float = unpack('<f', byte_array)[0]
        return python_float

class MyRadio(object):

    def __init__(self):
        self.q = Queue()
        self.poller = RadioPoller(self.q)
        self.poller.start()

    def has_data(self):
        return not self.q.empty()

    def get_data(self):
        readings = []
        while not self.q.empty():
            readings.append(self.q.get())
        return readings

class RadioPoller(Thread):
    '''A separate thread that constantly polls the RFM69 and places data in
    a queue, to be read by the owning MyRadio'''

    def __init__(self, result_queue, sleep_time=.05):
        Thread.__init__(self, name='rfm69_poller')
        self.q = result_queue
        self.sleep_time = sleep_time

    def run(self):
        # just to make the library shutup about using pins already in use...
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        
        with Radio(FREQ_915MHZ,
                   THIS_NODE_ID,
                   NETWORK_ID,
                   isHighPower=False,
                   verbose=False) as radio:

            #set bitrate to 1.2kbps from library default of 55kbps
            # The minimum RSSI value that gets through goes down,
            # Demonstrating that it is more robust
            radio._writeReg(0x03, 0x68)
            radio._writeReg(0x04, 0x2B)

            # enable pre-amp on receiver, increasing sensitivty and range
            # to verfiy, place Tx and RX in non moving locations, and print RSSI
            # values with this used and without it. There should be a 2-4 dB
            # benefit from using the pre-amp
            # lowpowerlab.com/forum/rf-range-antennas-rfm69-library/rfm69hw-range-test!
            radio._writeReg(0x58, 0x2D)

            while True:
                # print("RadioPoller is polling...")
                for packet in radio.get_packets():
                    # entry = (int(packet.RSSI), packet.received
                    # print("RadioPoller received some data!")
                    logger.debug("got a radio packet with rssi={}".format(packet.RSSI))
                    self.q.put(packet.data[:])
                    # print (packet.RSSI, bytes2floats(packet.data))

                time.sleep(self.sleep_time)
