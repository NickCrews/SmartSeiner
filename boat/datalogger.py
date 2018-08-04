

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
            print(merged_data)
            if merged_data['datetime'] is not np.nan:
                # print("writing data: {}",format(merged_data))
                print('writing data...')
                self.write_line(merged_data)
            time.sleep(10)

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
        merged['skiff_speed']   = skiff_data['speed']
        merged['boat_lat']      = boat_data['lat']
        merged['boat_lon']      = boat_data['lon']
        merged['boat_heading']  = boat_data['heading']
        merged['boat_COG']      = boat_data['COG']
        merged['boat_speed']    = boat_data['speed']
        merged['pressure']      = boat_data['pressure']
        merged['temp']          = boat_data['temp']
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
        # verify file has correct column headers...
        with open(filename, 'r') as fp:
            #get the first line, strip the ending newline, and split on tabs
            file_columns = fp.readline().strip().split('\t')
            assert column_names == file_columns
        with open(filename, 'a') as fp:
            entries = [str(data[col]) for col in column_names]
            line = '\t'.join(entries)
            fp.write(line)
            fp.write('\n')
