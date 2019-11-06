"""
    Generates polynomial from secret string with use of CRC encoding
"""

from bitstring import BitArray
import binascii

from Galois.Galois_Converter import GaloisConverter
from Galois.Galois_Field import GF


class PolynomialGenerator:
    def __init__(self, secret_bytes, degree, crc_length, gf_exp):
        """
        :param secret_bytes: secret in bytes format
        :param degree: polynomial degree as int
        :param crc_length: CRC length as int
        :param gf_exp: exponential in GF(2**gf_exp)
        """
        self.degree = degree
        self.crc_length = crc_length
        self.secret_bit = BitArray(bytes=secret_bytes, length=len(secret_bytes) * 8)
        self.gf_exp = gf_exp

        self.checksum_bit = BitArray(uint=binascii.crc32(self.secret_bit.bytes), length=self.crc_length)

        # join secret bitstring with CRC
        self.total_bit = self.secret_bit.copy()
        self.total_bit.append(self.checksum_bit)

        self.coefficients = self.extract_coefficients()
        # save polynomial in GF 2**32 form for performance reasons
        self.poly_gf_32 = GaloisConverter.convert_int_list_to_gf_2_list(self.coefficients, 32)
        # save galois field K for polynomial evaluations
        self.K = GF(2, gf_exp)

    def prune_secret(self, secret_bit):
        """ Prunes secret if secret length + CRC length is not multiple of
            polynomial degree + 1. Takes secret as BitArray
            :returns pruned secret as Bitarray """
        # check if bitstring has multiple of length of polynomial degree
        # secret is pruned if length don't match multiple of polynomial degree + 1
        remainder = (len(secret_bit) + self.crc_length) % (self.degree + 1)
        secret_len = len(secret_bit) - remainder
        if remainder == 0:
            return secret_bit
        else:
            return secret_bit[0:secret_len]

    def extract_coefficients(self):
        """ extracts coefficients of polynomial from bitstring
            :returns coefficients as list """
        # split to parts, convert to uint and add to list
        coefficients = []
        assert len(self.total_bit) % (self.degree + 1) == 0
        step = int(len(self.total_bit) / (self.degree + 1))
        for i in range(0, len(self.total_bit), step):
            # print(len(self.total_bit[i:i + step]))
            # print(self.total_bit[i:i + step].bin)
            # print(self.total_bit[i:i + step].uint)
            coefficients.append(self.total_bit[i:i + step].uint)
        return coefficients

    def evaluate_polynomial_gf_2(self, x):
        """ Evaluate polynomial of this polynomial generator at x in GF(2**m)
            :param x: int
            :param m: exponential in GF(2**m)
            :returns function result as int """
        m = self.gf_exp
        if m == 32:
            poly_gf = self.poly_gf_32
        else:
            poly_gf = GaloisConverter.convert_int_list_to_gf_2_list(self.coefficients, m)
        x_gf = GaloisConverter.convert_int_to_element_in_gf_2(x, m)
        y_gf = self.K.eval_poly(poly_gf, x_gf)
        result = GaloisConverter.convert_gf_2_element_to_int(y_gf, m)
        # Safety check
        if result > 2**m*2:
            raise ValueError('Too large number generated in polynomial GF(2**{}):{}'.format(m, result))
        return result

    def evaluate_polynomial_gf_2_array(self, array):
        """ Evaluate polynomial on list of integers
            :param array: list of integers
            :param m: exponential in GF(2**m) """
        result = []
        for x in array:
            result.append(self.evaluate_polynomial_gf_2(x))
        return result
