#compass.py
import time
import numpy as np

import Adafruit_LSM303
#hookup from Pi to lsm303
#5v        <---> Vin
#GND       <---> GND
#Pin3(SDA) <---> SDA
#Pin5(SCL) <---> SCL

from ellipsoid_fit import ellipsoid_fit, data_regularize

class BoatCompass(object):

    def __init__(self, calibration_file=None):
        self.lsm303 = Adafruit_LSM303.LSM303()
        if calibration_file:
            self.compass = load_compass(calibration_file)
        else:
            self.compass = Compass(declination=13,
                                   calibration_params=None)

    def get_raw_data(self):
        acc, mag =  self.lsm303.read()
        return mag

    def correct(self, raw_data):
        return self.compass.correct(raw_data)

    def get_corrected(self):
        raw = self.get_raw_data()
        return self.correct(raw)

    def calc_heading(self, corrected):
        return self.compass.heading(corrected)

    def get_heading(self):
        raw = self.get_raw_data()
        corrected = self.correct(raw)
        # mag_x, mag_z, mag_y = mag
        return self.compass.heading(corrected)

    def calibrate(self, duration=15):
        start = time.time()
        readings = []
        print("rotate the compass through all orientations for {} seconds...".format(duration),
            end='',
            flush=True)
        while time.time()-start < duration:
            readings.append(self.get_raw_data())
        print("done.")
        array = np.array(readings)
        self.compass.calibrate(array)

    def save(self, filename):
        self.compass.save(filename)

    def __repr__(self):
        center, radii, evecs, v = self.compass.params
        args = self.compass.declination, center, radii, evecs, v
        return "BoatCompass (declination={}, center={}, radii={}, evecs={}, v={})".format(*args)

class Compass(object):
    '''Abstraction that takes raw acceleration and magnetometer readings,
    finds a calibration for them mapping from the ellipsoid to a sphere,
    can correct using the calibration, add declination,
    and can save and load these parameters.'''


    def __init__(self, declination=0, calibration_params=None):
        self.declination = declination
        if calibration_params is None:
            center = 0,0,0
            evecs  = 0,0,0
            radii  = 1,1,1
            v = None
            calibration_params = center, evecs, radii, v
        self.params = calibration_params

    @staticmethod
    def _default_params():
        '''Generate the default params that don't affect readings'''
        readings = []
        for i in range(10000):
            x = np.random.random()*2-1
            y = np.random.random()*2-1
            z = 1 - np.sqrt(x*x + y*y)
            if np.random.random() > .5:
                z = -z
            readings.append([x,y,z])
        readings = np.array(readings)
        regularized = data_regularize(readings, divs=8)
        return ellipsoid_fit(regularized)

    def calibrate(self, raw_mag):
        #not sure what regularizing does but the ellipsoid_fit example uses it...
        regularized = data_regularize(raw_mag, divs=8)
        center, radii, evecs, v = ellipsoid_fit(regularized)
        self.params = center, radii, evecs, v

    def correct(self, raw_mag):
        center, radii, evecs, v = self.params
        raw_mag = np.array(raw_mag)
        centered = raw_mag - center.T

        a,b,c = radii
        r = (a*b*c)**(1./3.)#preserve volume?
        D = np.array([[r/a,0.,0.],[0.,r/b,0.],[0.,0.,r/c]])
        #http://www.cs.brandeis.edu/~cs155/Lecture_07_6.pdf
        #affine transformation from ellipsoid to sphere (translation excluded)
        TR = evecs.dot(D).dot(evecs.T)
        transformed = TR.dot(centered.T).T
        # if its just one row of data then keep it 1D
        if transformed.shape[0] == 1:
            return transformed[0]
        else:
            return transformed

    def heading(self, data):
        data = np.array(data)
        if len(data.shape) == 1:
            x,y,z = data
        else:
            x,y,z = data.T
        # print(x, y, x*x+y*y)

        heading = np.arctan2(y,x) * (180/np.pi)
        heading += self.declination
        heading %= 360
        return heading

    def save(self, filename):
        import os
        dir = os.path.dirname(filename)
        if dir != '':
            os.makedirs(dir, exist_ok=True)
        center, radii, evecs, v = self.params
        d = dict(declination=self.declination,
                 center=center.tolist(),
                 radii=radii.tolist(),
                 evecs=evecs.tolist(),
                 v=v.tolist())
        import json
        with open(filename, 'w') as fp:
            json.dump(d, fp, indent=4, sort_keys=True)

    def __repr__(self):
        center, radii, evecs, v = self.params
        args = self.declination, center, radii, evecs, v
        return "Compass (declination={}, center={}, radii={}, evecs={}, v={})".format(*args)

def load_compass(filename):
    import json
    with open(filename) as fp:
        try:
            param_dict = json.load(fp)

            declination = param_dict['declination']
            params = (np.array(param_dict['center']),
                      np.array(param_dict['radii']),
                      np.array(param_dict['evecs']),
                      np.array(param_dict['v']))
            # print()
            # for p in params:
            #     print(p)
            #     print(np.array(p))
            #
            # print()
            c = Compass(declination=declination, calibration_params=params)
            return c
        except:
            raise Exception("Bad Compass parameter file")
