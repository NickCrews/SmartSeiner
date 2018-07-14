'''
bigboat.py
The main entry point for the code run the Raspberry Pi on the big boat.
Listens for data from the skiff, filters it, and saves it for later analysis.

dependencies:
github.com/jkittley/RFM69
'''

import time
from math import sin, cos, sqrt, atan2, radians

from RFM69 import Radio, FREQ_915MHZ
import Adafruit_LSM303

# which network, and which node upon that network, is this RPi
NETWORK_ID = 42
NODE_ID = 42

def distance(loc1, loc2):
    '''return the distance between two lat/long pairs. Assumes earth is sphere.
    https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude'''
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # approximate radius of earth in m
    R = 6373.0 * 1000
    return R * c

def is_skiff_trailing(skiff_loc, boat_loc):
    pass

def has_set_started(skiff_locs, boat_locs):
    pass

def has_closed_up(skiff_locs, boat_locs):
    pass

def main():
    with Radio(FREQ_915MHZ, nodeID=NODE_ID, networkID=NETWORK_ID, verbose=True) as radio:
        while True:
            print()
            for packet in radio.get_packets():
                print(packet)
            time.sleep(3)

if __name__ == '__main__':
    print("BEGINNING MAIN")
    main()



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
