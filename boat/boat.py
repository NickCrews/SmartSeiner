'''
bigboat.py
The main entry point for the code run the Raspberry Pi on the big boat.
Listens for data from the skiff, filters it, and saves it for later analysis.

dependencies:
github.com/jkittley/RFM69
'''

import time
import numpy as np

from gps3 import gps3 #https://pypi.org/project/gps3/
#hookup from Pi to Adafruit Ultimate GPS
#5v        <---> Vin
#GND       <---> GND
#Pin8(TX)  <---> RX
#Pin10(RX) <---> TX

import compass

class Boat(object):

    DEFAULT_CALIBRATION_FILE_PATH = "./calibrations/boat.txt"

    def __init__(self, compass_file=None):

        #assumes gpsd daemon has already been started
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

        self.compass = compass.BoatCompass(compass_file)

    def get_heading(self):
        # Read the X, Y, Z axis acceleration values and print them.
        accel, mag = self.lsm303.read()
        # Grab the X, Y, Z components from the reading and print them out.
        accel_x, accel_y, accel_z = accel
        mag_x, mag_z, mag_y = mag
        return self.compass.get_heading(mag)

    def get_location(self):
        self._update()
        coords = self.data_stream.TPV['lat'], self.data_stream.TPV['lon']
        return coords

    def get_COG(self):
        self._update()
        return self.data_Stream.TPV['heading']

    def get_time(self):
        self._update()
        return self.data_stream.TPV['time']

    def _update(self):
        for new_data in self.gps_socket:
            if new_data:
                self.data_stream.unpack(new_data)
            return

if __name__ == '__main__':
##    import time
##    print("Beginning boat test")
    boat = Boat()
##    while True:
##        print(boat.get_location())
##        print(boat.get_time())
##        print(boat.get_heading())
##        time.sleep(1)
    print("rotate boat compass in all directions for 15 seconds...")
    boat.calibrate_compass()








'''
Every 10 seconds, request data from the skiff.
Save this data into a rotating buffer so we always have the last 4 hours
Look through this and see if a Set occured by looking for the notable points:
- the let go
- full extension of net
- starting to close up
- closed up
- skiff hooked back up
If one did, save this as a Set
'''
