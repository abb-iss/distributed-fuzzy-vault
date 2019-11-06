"""
    Minutia classes according to output of different algorithms

    Current supported minutiae detection algorithms:
    - NBIS MINDTCT
"""

import math


class Minutia:
    # boundaries of Minutia coordinates
    X_MIN = 0
    X_MAX = 0
    Y_MIN = 0
    Y_MAX = 0
    # orientation of theta is 0 horizontally to the right
    THETA_MIN = 0
    THETA_MAX = 0

    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def __str__(self):
        return 'x = {}\n' \
            'y = {}\n' \
            'theta = {}\n'.format(self.x, self.y, self.theta)

    def __repr__(self):
        return '{}({}, {}, {})'.format(
            self.__class__.__name__, self.x, self.y, self.theta
        )

    def is_zero(self):
        """
        Determines if minutia attributes are all zero (x, y and theta all 0)
        :returns: True if all minutia attributes are zero
        """
        return self.x == 0 and self.y == 0 and self.theta == 0

    def distance_to(self, minutia):
        return int(math.sqrt(abs(self.x - minutia.x) ** 2 + abs(self.y - minutia.y) ** 2))


class MinutiaNBIS(Minutia):
    # boundaries of Minutia coordinates
    X_MIN = 0
    X_MAX = 560
    Y_MIN = 0
    Y_MAX = 560
    THETA_MIN = 0
    THETA_MAX = 360
    QUALITY_MIN = 0
    QUALITY_MAX = 100

    def __init__(self, x, y, theta, quality=0, limit=True):
        if limit:
            assert self.X_MIN <= x <= self.X_MAX
            assert self.Y_MIN <= y <= self.Y_MAX
        assert self.THETA_MIN <= theta <= self.THETA_MAX
        assert self.QUALITY_MIN <= quality <= self.QUALITY_MAX
        super(MinutiaNBIS, self).__init__(x, y, theta)
        self.quality = quality

    def __str__(self):
        return super(MinutiaNBIS, self).__str__() + \
            'quality = {}\n'.format(self.quality)


class MinutiaNBIS_GH(MinutiaNBIS):
    """ Minutia for Geometric Hashing using Minutia of NBIS """
    # boundaries of Minutia coordinates moved so that origin (0,0) is in the center (not in left lower corner)
    # x/y coordinates are in -MIN/2 to MAX/2 after conversion from MinutiaNBIS
    # due to translation in geometric hashing, the position extends to (2**(1/2)*(CONVERT_MAX - CONVERT_MIN))
    # where 2**(1/2) is max of cos(theta)+sin(theta) and 500 max difference
    X_CONVERT_MIN = int((MinutiaNBIS.X_MIN - MinutiaNBIS.X_MAX) / 2)
    X_CONVERT_MAX = int((MinutiaNBIS.X_MAX - MinutiaNBIS.X_MIN) / 2)
    Y_CONVERT_MIN = int((MinutiaNBIS.Y_MIN - MinutiaNBIS.Y_MAX) / 2)
    Y_CONVERT_MAX = int((MinutiaNBIS.Y_MAX - MinutiaNBIS.Y_MIN) / 2)
    X_MIN = int(2**(1/2) * (X_CONVERT_MIN - X_CONVERT_MAX))
    X_MAX = int(2**(1/2) * (X_CONVERT_MAX - X_CONVERT_MIN))
    Y_MIN = int(2**(1/2) * (Y_CONVERT_MIN - Y_CONVERT_MAX))
    Y_MAX = int(2**(1/2) * (Y_CONVERT_MAX - Y_CONVERT_MIN))
    THETA_MIN = MinutiaNBIS.THETA_MIN
    THETA_MAX = MinutiaNBIS.THETA_MAX
    QUALITY_MIN = MinutiaNBIS.QUALITY_MIN
    QUALITY_MAX = MinutiaNBIS.QUALITY_MAX

    @staticmethod
    def convert_from_MinutiaNBIS(m: MinutiaNBIS):
        """ convert MinutiaNBIS to MinutiaNBIS_GH """
        # change coordinates to new coordinate system
        x = m.x - MinutiaNBIS_GH.X_CONVERT_MAX
        y = m.y - MinutiaNBIS_GH.Y_CONVERT_MAX
    
        assert MinutiaNBIS_GH.X_CONVERT_MIN <= x <= MinutiaNBIS_GH.X_CONVERT_MAX
        assert MinutiaNBIS_GH.Y_CONVERT_MIN <= y <= MinutiaNBIS_GH.Y_CONVERT_MAX
        assert MinutiaNBIS_GH.THETA_MIN <= m.theta <= MinutiaNBIS_GH.THETA_MAX
        assert MinutiaNBIS_GH.QUALITY_MIN <= m.quality <= MinutiaNBIS_GH.QUALITY_MAX
        return MinutiaNBIS_GH(x, y, m.theta, m.quality)
