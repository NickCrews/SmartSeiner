#main.py
import time
import datetime
import os
import numpy as np

import Adafruit_LSM303

import boat
import skiff
import compass

class DataLogger(object):

    def __init__(self):
        # self.boat = boat.Boat(compass_file=boat.Boat.DEFAULT_CALIBRATION_FILE_PATH)
        self.boat = boat.Boat(compass_file=None)
        # self.boat.compass.params = compass.Compass._default_params()
        self.skiff = skiff.Skiff()

    def begin(self):
        while True:
            print('getting data...')
            boat_data  = self.boat.get_data()
            skiff_data = self.skiff.get_data()
            merged_data = self.merge_data(boat_data, skiff_data)
            if merged_data['datetime'] is not np.nan:
                # print("writing data: {}",format(merged_data))
                self.write_line(merged_data)
            time.sleep(5)

    def merge_data(self, boat_data, skiff_data):
        merged = {}
        date_and_time = boat_data['datetime']
        if date_and_time is not np.nan:
            dt = datetime.datetime.strptime(date_and_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            # convert to alaska time
            dt = dt - datetime.timedelta(hours=8)
        else:
            dt = np.nan
        merged['datetime']      = dt
        merged['skiff_lat']     = skiff_data['lat']
        merged['skiff_lon']     = skiff_data['lon']
        merged['skiff_heading'] = skiff_data['heading']
        merged['skiff_COG']     = skiff_data['COG']
        merged['boat_lat']      = boat_data['lat']
        merged['boat_lon']      = boat_data['lon']
        merged['boat_heading']  = boat_data['heading']
        merged['boat_COG']      = boat_data['COG']
        return merged

    def write_line(self, data):
        if data['datetime'] is np.nan:
            raise Exception("Can only save data with a valid timestamp")
        day_string = str(data['datetime']).split(" ")[0]
        filename = 'data/' + day_string + '.csv'

        # make the directory and init the file if necessary
        dir = os.path.dirname(filename)
        if dir != '':
            os.makedirs(dir, exist_ok=True)
        column_names = list(sorted(data.keys()))
        if not os.path.exists(filename):
            with open(filename, 'w') as fp:
                line = '\t'.join(column_names)
                fp.write(line)
                fp.write('\n')
        with open(filename, 'a') as fp:
            entries = [str(data[col]) for col in column_names]
            line = '\t'.join(entries)
            fp.write(line)
            fp.write('\n')

def main():
    dl = DataLogger()
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
