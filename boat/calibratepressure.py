import time
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
        raise Exception("Could not initiate ms5803")

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
        raise Exception("Lost connection to ms5803")

if __name__ == '__main__':
    pg = PressureGauge()
    fname = "./calibrations/pressure_{}.csv".format(time.ctime().replace(':','-').replace(' ', '_'))
    with open(fname, 'w') as fp:
        buf = "time\tpress\ttemp"
        print(buf)
        fp.write(buf + '\n')
        while True:
            try:
                press, temp = pg.read()
            except OSError:
                continue
            buf = "{}\t{}\t{}".format(time.time(), press, temp)
            print(buf)
            fp.write(buf+'\n')
            time.sleep(5)
