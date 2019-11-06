"""
    Poly Ring by user6655984 on StackOverflow
    https://stackoverflow.com/questions/48065360/interpolate-polynomial-over-a-finite-field
"""

import itertools


class PolyRing:
    def __init__(self, field):
        self.K = field

    def add(self, p, q):
        s = [self.K.add(x, y) for x, y in itertools.zip_longest(p[::-1], q[::-1], fillvalue=[])]
        return s[::-1]

    def sub(self, p, q):
        s = [self.K.sub(x, y) for x, y in itertools.zip_longest(p[::-1], q[::-1], fillvalue=[])]
        return s[::-1]

    def mul(self, p, q):
        if len(p) < len(q):
            p, q = q, p
        s = [[]]
        for j, c in enumerate(q):
            s = self.add(s, [self.K.mul(b, c) for b in p] + [[]] * (len(q) - j - 1))
        return s
