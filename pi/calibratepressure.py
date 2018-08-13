import time
from pressuregauge import PressureGauge

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
