#compass.py

import math
from ellipsoid_fit import ellipsoid_fit, data_regularize

class Compass(object):

    def __init__(self, declination=0, calibration_params=None):
        self.declination = declination
        if calibration_params is None:
            center = 0,0,0
            evecs  = 0,0,0
            radii  = 1,1,1
            v = None
            calibration_params = center, evecs, radii, v
        self.params = calibration_params

    def calibrate(self, raw_mag):
        #not sure what regularizing does but the ellipsoid_fit example uses it...
        regularized = data_regularize(raw_mag, divs=8)
        center, radii, evecs, v = ellipsoid_fit(regularized)
        self.params = center, radii, evecs, v

    def correct_readings(self, raw_mag):
        center, radii, evecs, v = self.params
        centered = raw_mag - center.T

        a,b,c = radii
        r = (a*b*c)**(1./3.)#preserve volume?
        D = np.array([[r/a,0.,0.],[0.,r/b,0.],[0.,0.,r/c]])
        #http://www.cs.brandeis.edu/~cs155/Lecture_07_6.pdf
        #affine transformation from ellipsoid to sphere (translation excluded)
        TR = evecs.dot(D).dot(evecs.T)
        transformed = TR.dot(centered.T).T
        return transformed

    def get_heading(self, raw_mag):
        corrected = self.correct_readings(raw_mag)
        x,y,z = corrected
        heading = math.atan2(y,x) * (180/math.pi)
        heading += self.declination
        heading %= 360
        return heading

    def save(self, filename):
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write(str(self.declination))
            f.write(str(self.params))

    def __repr__(self):
        center, radii, evecs, v = self.params
        args = self.declination, center, radii, evecs, v
        return "Compass (declination={}, center={}, radii={}, evecs={}, v={})".format(*args)

def load(filename):
    with open(filename) as f:
        try:
            declination, params = f.read()
        except:
            raise Exception("Bad Compass paramter file")
