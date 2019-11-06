"""
    Galois Field by user6655984 on StackOverflow
    https://stackoverflow.com/questions/48065360/interpolate-polynomial-over-a-finite-field
"""

import itertools
from sympy.polys.domains import ZZ
from sympy.polys.galoistools import (gf_irreducible_p, gf_add, gf_sub, gf_mul, gf_rem, gf_gcdex)
from sympy.ntheory.primetest import isprime


class GF:
    def __init__(self, p, n=1):
        p, n = int(p), int(n)
        if not isprime(p):
            raise ValueError("p must be a prime number, not %s" % p)
        if n <= 0:
            raise ValueError("n must be a positive integer, not %s" % n)
        self.p = p
        self.n = n
        if n == 1:
            self.reducing = [1, 0]
        else:
            for c in itertools.product(range(p), repeat=n):
                poly = (1, *c)
                if gf_irreducible_p(poly, p, ZZ):
                    self.reducing = poly
                    break

    def add(self, x, y):
        return gf_add(x, y, self.p, ZZ)

    def sub(self, x, y):
        return gf_sub(x, y, self.p, ZZ)

    def mul(self, x, y):
        return gf_rem(gf_mul(x, y, self.p, ZZ), self.reducing, self.p, ZZ)

    def inv(self, x):
        s, t, h = gf_gcdex(x, self.reducing, self.p, ZZ)
        return s

    def eval_poly(self, poly, point):
        val = []
        for c in poly:
            val = self.mul(val, point)
            val = self.add(val, c)
        return val
