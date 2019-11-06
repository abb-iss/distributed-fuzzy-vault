"""
    Converter from int to Galois Field element and vice versa
"""

from bitstring import BitArray


class GaloisConverter:
    @staticmethod
    def convert_gf_2_element_to_int(gf_element: list, m: int):
        """ Converts element in GF(2**m) in the form of [1,0,0,0] to int
            polynomials represented by list of coefficients, highest degrees first
            :param gf_element: list of coefficients
            :param m: exponential of the Galois Field (2**m)
            :returns int """
        # safety check
        if len(gf_element) > m:
            raise ValueError('GF element length {} is bigger than can be encoded in GF(2**{})!'.format(gf_element, m))
        if not gf_element:
            return 0
        else:
            result = BitArray(length=len(gf_element))
            for p in gf_element:
                result.append(bin(p))
            return result.int

    @staticmethod
    def convert_gf_2_list_to_int_list(gf_2_list: list, m: int):
        """ Converts list of GF(2**m) elements to list of integers
            :returns list of integers """
        result = []
        for element in gf_2_list:
            result.append(GaloisConverter.convert_gf_2_element_to_int(element, m))
        return result

    @staticmethod
    def convert_int_to_element_in_gf_2(x: int, m: int):
        """ Converts int to element in GF(2**m) in the form of [1,0,0,0]
            polynomials represented by list of coefficients, highest degrees first
            :param x: int
            :param m: exponential of the Galois Field (2**m)
            :returns GF(2**m) element in the form of [1,0,0,0] """
        # safety check
        if x > 2**m:
            raise ValueError('Integer %d is bigger than can be encoded in GF(2**%d)!' % (x, m))
        result = []
        for bit in format(x, 'b'):
            result.append(int(bit))
        return result

    @staticmethod
    def convert_int_list_to_gf_2_list(int_list: list, m: int):
        """ Converts list of integers to list of GF(2**m) elements
            :returns list of GF(2**m) elements (list of coefficients) """
        result = []
        for element in int_list:
            result.append(GaloisConverter.convert_int_to_element_in_gf_2(element, m))
        return result
