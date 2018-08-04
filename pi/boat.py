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
import ms5803py

class PressureGauge(ms5803py.Sensor):
    '''Cuz the ms5803 is connected to the pi via a 30ft telephone cable,
    since the ms5803 is in the fishhold, the I2C connection is bad.
    However, just retrying all communications a few times seems to work.'''

    def __init__(self, *args, **kwargs):
        RETRIES = 15
        for _ in range(RETRIES):
            try:
                return super().__init__(*args, **kwargs)
            except OSError:
                # print('retrying to init ms5803...')
                pass #we just gotta try again
            time.sleep(.1)
        raise OSError("Could not initiate ms5803")

    def read(self):
        RETRIES = 25
        for _ in range(RETRIES):
            try:
                pressure, temp = super().read()
                if pressure > 50 and pressure < 10000:
                    # sometimes theres a bogus pressure reading of like -800?
                    return pressure, temp
            except OSError:
                # print('re-reading from ms5803...')
                time.sleep(.1)
                pass #we just gotta try again
        raise OSError("Lost connection to ms5803")

class Boat(object):

    DEFAULT_CALIBRATION_FILE_PATH = "./calibrations/boat.txt"

    def __init__(self, compass_file=None):

        #assumes gpsd daemon has already been started
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

        self.compass = compass.BoatCompass(compass_file)
        self.pressure_gauge = PressureGauge()
        self.has_new_data = False

    def get_heading(self):
        return self.compass.get_heading()

    def get_location(self):
        self._update()
        coords = self.data['lat'], self.data['lon']
        return coords

    def get_COG(self):
        self._update()
        return self.data['heading']

    def get_time(self):
        self._update()
        return self.data['time']

    def get_data(self):
        '''Try to read new data from GPS, and then pull out some useful info

        All of the available attributes are at http://www.catb.org/gpsd/gpsd_json.html
        '''
        self._update()
        data = {}
        data['lat']        = self.data['lat']
        data['lon']        = self.data['lon']
        data['datetime']   = self.data['time'] #Time/date stamp in ISO8601 format, UTC.
        data['COG']        = self.data['track']
        data['speed']      = self.data['speed']
        data['heading']    = self.compass.get_heading()
        try:
            pressure, temp = self.pressure_gauge.read()
        except OSError:
            # sometimes we just lose a connection, forget it for now
            pressure, temp = np.nan, np.nan
        data['pressure']   = pressure
        data['temp']       = temp
        self.has_new_data = False
        return data

    def _update(self):
        for new_data in self.gps_socket:
            if new_data:
                self.data_stream.unpack(new_data)
                self.data = {}
                for (key, value) in self.data_stream.TPV.items():
                    if value == 'n/a':
                        value = np.nan
                    self.data[key] = value
                self.has_new_data = True
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
