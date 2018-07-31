import time
import ms5803py

class PressureGauge(ms5803py.Sensor):
    '''Cuz the ms5803 is connected to the pi via a 30ft telephone cable,
    since the ms5803 is in the fishhold, the I2C connection is bad.
    However, just retrying all communications a few times seems to work.'''

    def __init__(self, *args, **kwargs):
        RETRIES = 5
        for _ in range(RETRIES):
            try:
                return super().__init__(*args, **kwargs)
            except OSError:
                # print('retrying to init ms5803...')
                pass #we just gotta try again
        raise Exception("Could not initiate ms5803")

    def read(self):
        RETRIES = 5
        for _ in range(RETRIES):
            try:
                return super().read()
            except OSError:
                # print('re-reading from ms5803...')
                pass #we just gotta try again
        raise Exception("Lost connection to ms5803")

if __name__ == '__main__':
    pg = PressureGauge()
    print("time\tpress\ttemp")
    while True:
        press, temp = pg.read()
        print("{}\t{}\t{}".format(time.time(), press, temp))
        time.sleep(.2)
