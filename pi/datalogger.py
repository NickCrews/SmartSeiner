import time
import datetime
import os

import numpy as np
# import pandas as pd

from boat import Boat
from skiff import Skiff

class DataLogger(object):

    def __init__(self, log_interval=10, sample_interval=1):
        # self.boat = boat.Boat(compass_file=boat.Boat.DEFAULT_CALIBRATION_FILE_PATH)
        self.boat = Boat(compass_file=None)
        # self.boat.compass.params = compass.Compass._default_params()
        self.skiff = Skiff()
        self.sample_interval = sample_interval
        self.log_interval = log_interval
        self.filename = None

    def make_log_file(self, data):
        day_string = str(data['datetime']).split(" ")[0]
        self.filename = 'data/' + day_string + '.csv'

        # make the directory and init the file if necessary
        dir = os.path.dirname(self.filename)
        if dir != '':
            os.makedirs(dir, exist_ok=True)
        column_names = list(sorted(data.keys()))
        header = '\t'.join(column_names) + '\n'
        print(header, end='')
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as fp:
                fp.write(header)

    def begin(self):
        last_sample = time.time()
        last_log  = time.time()
        samples = []
        while True:
            current_time = time.time()
            if current_time - last_sample > self.sample_interval:
                boat_data  = self.boat.get_data()
                skiff_data = self.skiff.get_data()
                merged_data = self.merge_boat_and_skiff_data(boat_data, skiff_data)
                samples.append(merged_data)
                last_sample = current_time
            if current_time - last_log > self.log_interval:
                merged = self.merge_samples(samples)
                if merged['datetime'] is not np.nan:
                    # print("writing data: {}",format(merged_data))
                    self.write_line(merged)
                    samples = []
                    last_log = current_time
            time.sleep(.1)

    def merge_samples(self, samples):
        # print('raw samples:')
        # print(samples)

        def mean_column(column_name):
            # print('series:', column_name)
            series = np.array([s[column_name] for s in samples], dtype=np.float64)
            # print(series)
            series = series[np.isfinite(series)] #remove nans
            if series.size == 0:
                return np.nan
            # sometimes there are super bogus entries, no idea why
            # keep entries only within CUTOFF std deviations of mean
            std_dev = np.std(series)
            if std_dev != 0:
                dev = series - np.mean(series)
                num_sigmas = np.absolute(dev / std_dev)
                CUTOFF = 5
                series = series[num_sigmas<CUTOFF]
            # print(series)
            if series.size > 0:
                return series.mean()
            else:
                return np.nan

        result = {}
        for sample in samples:
            if isinstance(sample['datetime'], datetime.datetime):
                result['datetime'] = sample['datetime']
                break

        columns = ['skiff_lat',
                   'skiff_lon',
                   'skiff_COG',
                   'skiff_speed',
                   'boat_lat',
                   'boat_lon',
                   'boat_COG',
                   'boat_speed',
                   'pressure',
                   'temp']
        for col_name in columns:
            result[col_name] = mean_column(col_name)

        # print('meaned result:')
        # print(result)
        return result

        # df = pd.concat(samples)
        # print("samples df")
        # print(df)
        # meaned = df.mean(axis=1)
        # print('meaned')
        # print(meaned)
        # return meaned

    def merge_boat_and_skiff_data(self, boat_data, skiff_data):
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
        # merged['skiff_heading'] = skiff_data['heading']
        merged['skiff_COG']     = skiff_data['COG']
        merged['skiff_speed']   = skiff_data['speed']
        merged['boat_lat']      = boat_data['lat']
        merged['boat_lon']      = boat_data['lon']
        # merged['boat_heading']  = boat_data['heading']
        merged['boat_COG']      = boat_data['COG']
        merged['boat_speed']    = boat_data['speed']
        merged['pressure']      = boat_data['pressure']
        merged['temp']          = boat_data['temp']
        return merged

    def write_line(self, data):
        if data['datetime'] is np.nan:
            raise Exception("Can only save data with a valid timestamp")
        if not self.filename:
            self.make_log_file(data)

        # verify file has correct column headers...

        with open(self.filename, 'r') as fp:
            #get the first line, strip the ending newline, and split on tabs
            file_columns = fp.readline().strip().split('\t')
            column_names = list(sorted(data.keys()))
            assert column_names == file_columns
        with open(self.filename, 'a') as fp:
            entries = [str(data[col]) for col in column_names]
            line = '\t'.join(entries) + '\n'
            fp.write(line)
            print(line, end='')
