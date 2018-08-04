#main.py
import time
import datetime
import os
import numpy as np

import Adafruit_LSM303

import boat
import skiff
import compass

import datalogger



def main():
    dl = datalogger.DataLogger()
    dl.begin()

def calibrate_boat():
    lsm303 = Adafruit_LSM303.LSM303()
    start = time.time()
    readings = []
    print("rotate the compass through all orientations for 15 seconds...", end='')
    while time.time()-start < 15:
        accel, mag = lsm303.read()
        readings.append(mag)
    print("done.")
    array = np.array(readings)

    c = compass.Compass(declination=13)
    c.calibrate(array)
    print(c)
    c.save(boat.Boat.DEFAULT_CALIBRATION_FILE_PATH)

    c = compass.load(boat.Boat.DEFAULT_CALIBRATION_FILE_PATH)
    print(c)

# def calibrate_compass():
#     c = compass.BoatCompass()
#     c.calibrate(20)
#     print(c)
#     c.save(boat.Boat.DEFAULT_CALIBRATION_FILE_PATH)

def test_compass():
    c = compass.BoatCompass("good_boat.txt")
    print(c)
    while True:
        raw = c.get_raw_data()
        # print(raw)
        corrected = c.correct(raw)
        # print(corrected)
        hdg = c.calc_heading(corrected)
        print("raw={}, corr={}, hdg={}".format(raw, corrected, hdg))
        time.sleep(.5)

def echo_compass():
    c = compass.BoatCompass()
    data = []
    start = time.time()
    print("rotate the compass through all orientations for 15 seconds...", end='')
    while time.time()-start < 30:
        rdg = c.get_raw_data()
        data.append(rdg)
        print(rdg)
        time.sleep(.1)
    arr = np.array(data)
    np.savetxt("echoed.txt", arr)

# def fix_raw_readings():
#     arr = np.loadtxt("echoed.txt")
#     print(arr[:5])
#     x, z, y = arr.T
#     arr = np.array([x, y, z]).T
#     print(arr[:5])
#     np.savetxt("echoed.txt", arr)

def calibrate_compass():
    arr = np.loadtxt("echoed.txt")
    c = compass.Compass()
    c.calibrate(arr)
    c.save("good_boat.txt")
    # c2 = compass.load_compass("good_boat.txt")
    # corrected = c2.correct(arr)
    # np.savetxt("corrected.txt", corrected)

if __name__ == '__main__':
    print("BEGINNING MAIN")
    # print(compass.Compass._default_params())
    main()
    # fix_raw_readings()
    # echo_compass()
    # correct_points()
    # calibrate_compass()
    # test_compass()
    # print(compass.Compass._default_params())
