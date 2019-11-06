"""
    Converter for Minutia
    - to bitstring and vice-versa
    - from bitstring to int and vice-versa
"""

from bitstring import BitArray
from Minutia import MinutiaNBIS, MinutiaNBIS_GH


class MinutiaConverter:
    def __init__(self, x_bit_length=11, y_bit_length=11, theta_bit_length=10, total_bit_length=32):
        self.X_BIT_LENGTH = x_bit_length
        self.Y_BIT_LENGTH = y_bit_length
        self.THETA_BIT_LENGTH = theta_bit_length
        self.TOTAL_BIT_LENGTH = total_bit_length

    def get_total_bitstring_from_minutia(self, minutia: MinutiaNBIS):
        """ Converts minutia to bitstring
        :returns BitArray """
        x_bit = BitArray(uint=int(minutia.x), length=self.X_BIT_LENGTH)
        y_bit = BitArray(uint=int(minutia.y), length=self.Y_BIT_LENGTH)
        theta_bit = BitArray(uint=int(minutia.theta), length=self.THETA_BIT_LENGTH)

        result_bit = x_bit.copy()
        result_bit.append(y_bit)
        result_bit.append(theta_bit)
        assert len(result_bit) == self.TOTAL_BIT_LENGTH
        return result_bit

    def get_uint_from_minutia(self, minutia: MinutiaNBIS, non_negative=True):
        """ Converts minutia to signed int
        :param minutia: Minutia to be encoded to uint
        :param non_negative: True if all coordinates in minutia are positive, else False (Minutia_NBIS_GH)
        :returns unsigned int """
        if not non_negative:
            return self.get_total_bitstring_from_minutia(
                MinutiaNBIS(minutia.x + minutia.X_MAX, minutia.y + minutia.Y_MAX, minutia.theta, limit=False)).uint
        else:
            return self.get_total_bitstring_from_minutia(minutia).uint

    def get_minutia_from_bitstring(self, bitstring: BitArray, non_negative=True):
        """ Recreates minutia from bitstring (BitArray)
        :param bitstring: bitstring to decode to minutia
        :param non_negative: True if all coordinates in minutia are positive, else False (Minutia_NBIS_GH, from storage)
        :returns Minutia with unsigned integer values """
        assert len(bitstring) == self.TOTAL_BIT_LENGTH
        x = bitstring[0:self.X_BIT_LENGTH].uint
        y = bitstring[self.X_BIT_LENGTH:self.X_BIT_LENGTH + self.Y_BIT_LENGTH].uint
        theta = bitstring[
                self.X_BIT_LENGTH + self.Y_BIT_LENGTH:self.X_BIT_LENGTH + self.Y_BIT_LENGTH + self.THETA_BIT_LENGTH].uint
        if not non_negative:
            x -= MinutiaNBIS_GH.X_MAX
            y -= MinutiaNBIS_GH.Y_MAX
        return MinutiaNBIS(x, y, theta)

    def get_minutia_from_uint(self, unsigned_int, non_negative=True):
        """ Recreates minutia from unsigned int that was created from bitstring
        :param unsigned_int: representation of minutia
        :param non_negative: True if all coordinates in minutia are positive, else False (Minutia_NBIS_GH, from storage)
        :returns Minutia """
        total_bit = BitArray(uint=unsigned_int, length=self.TOTAL_BIT_LENGTH)
        return self.get_minutia_from_bitstring(total_bit, non_negative=non_negative)
