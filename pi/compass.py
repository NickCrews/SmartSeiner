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
        # WATCH OUT FOR THIS ORDER, Z and Y are switched in the Adafruit lib!
        magX, magZ, magY = mag
        return magX, magY, magZ

    def correct(self, raw_data):
        return self.compass.correct(raw_data)

    def get_corrected(self):
        try:
            raw = self.get_raw_data()
        except OSError:
            # got an I2C error, just give a nan
            return np.nan
        return self.correct(raw)

    def calc_heading(self, corrected):
        return self.compass.heading(corrected)

    def get_heading(self):
        try:
            raw = self.get_raw_data()
        except OSError:
            # got an I2C error, just give a nan
            raise OSError("lost connection to compass!")
        # print(self)
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
            # don't perform a transformation
            center = np.array([[0,0,0]]).T
            radii  = np.array([1,1,1])
            evecs  = np.array([[1,0,0],
                               [0,1,0],
                               [0,0,1]])
            v = np.array([[1,1,1],
                          [0,0,0],
                          [0,0,0]])
            calibration_params = center, radii, evecs, v
        self.params = calibration_params

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
        if len(raw_mag.shape) == 1:
            return transformed[0]
        else:
            return transformed

    def heading(self, data):
        data = np.array(data)
        if len(data.shape) == 1:
            #TODO WTF the y and z order is revered??!!
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

def _monte_carlo_identity():
    '''Generate the default params that don't affect readings by fitting to a unit sphere'''
    # create points randomly distributed on the unit sphere
    npoints = 25000
    vec = np.random.randn(3, npoints)
    vec /= np.linalg.norm(vec, axis=0)
    # use those to fit
    regularized = data_regularize(vec.T, divs=8)
    return ellipsoid_fit(regularized)

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
