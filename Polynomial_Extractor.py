"""
    Polynomial Extractor extracts a polynomial from points with interpolation
    It also provides methods to verify if the extracted polynomial (secret) is correct using CRC or Hash

    interpolate_lagrange_poly_in_field by user6655984 on StackOverflow
    https://stackoverflow.com/questions/48065360/interpolate-polynomial-over-a-finite-field
"""

from functools import reduce
from bitstring import BitArray
import binascii
from itertools import combinations
from random import shuffle, sample
from math import factorial

import Constants
from Vault import Vault
from Galois.Poly_Ring import PolyRing
from Galois.Galois_Converter import GaloisConverter
from Galois.Galois_Field import GF


class PolynomialExtractor:
    def __init__(self, gf_exp):
        """
        :param gf_exp: exponential in GF(2**gf_exp)
        """
        self.gf_exp = gf_exp
        self.K = GF(2, gf_exp)

    def extract_polynomial_gf_2(self, X, Y):
        """ Extracts polynomial from X and Y using Lagrange interpolation over field K = GF(2**m) """
        poly = self.interpolate_lagrange_poly_in_field(X, Y)
        return GaloisConverter.convert_gf_2_list_to_int_list(poly, self.gf_exp)

    def interpolate_lagrange_poly_in_field(self, X, Y):
        """ Interpolates polynomial with Lagrange
            :param X: x-coordinates of points
            :param Y: y-coordinates of points
            :param K: Galois Field
            :returns polynomial in [1,0,0,0] form in GF K """
        R = PolyRing(self.K)
        poly = [[]]
        for j, y in enumerate(Y):
            Xe = X[:j] + X[j + 1:]
            numerator = reduce(lambda p, q: R.mul(p, q), ([[1], self.K.sub([], x)] for x in Xe))
            denominator = reduce(lambda x, y: self.K.mul(x, y), (self.K.sub(X[j], x) for x in Xe))
            poly = R.add(poly, R.mul(numerator, [self.K.mul(y, self.K.inv(denominator))]))
        return poly

    @staticmethod
    def check_crc_in_poly(poly, degree, crc_length, secret_length):
        """ Extract bitstring from polynomial coefficients and checks if CRC is correct
            :param poly: list of coefficients of polynomial
            :param degree: degree of the polynomial
            :param crc_length: length of the CRC in bits as int
            :param secret_length: length of the secret in bits as int
            :returns if CRC in polynomial encoding (secret) is correct as boolean"""
        # strip leading coefficients that are greater than degree + 1
        poly = poly[len(poly) - (degree + 1):]
        result = BitArray()
        assert (crc_length + secret_length) % (degree + 1) == 0
        coefficient_length = (crc_length + secret_length) // (degree + 1)
        for coefficient in poly:
            # if coefficient is bigger than supposed to CRC is definitely not correct
            if coefficient.bit_length() > coefficient_length:
                return False
            result.append(BitArray(uint=coefficient, length=coefficient_length))
        crc_code = result[-crc_length:]
        extracted_crc = crc_code.uint
        secret = result[:-crc_length]
        calculated_crc = binascii.crc32(secret.bytes)
        return extracted_crc == calculated_crc

    def interpolate_and_check_crc(self, vault: Vault, degree: int, crc_length, secret_length, log_dict,
                                  echo=False):
        """ Gets candidate points from vaults and interpolates on subsets in order
            to verify CRC (coordinates from interpolated polynomial consists of secret and CRC.
            If CRC matches, then match is found (vault is opened).
            :param vault: decoded vault
            :param degree: degree of polynomial
            :param gf_exp: exponential in GF(2**gf_exp)
            :param crc_length: length of CRC
            :param secret_length: length of secret
            :param log_dict: dictionary for logging (logs amount of subsets that were evaluated if CRC matched)
            :param echo: if True, printing intermediate messages to console
            :returns True if match is found, False otherwise """

        def generate_all_subsets_version(candidate_tuples):
            """ Generating all subsets first before interpolating and checking CRC """
            # calculate all subsets using possible candidate vault tuples
            subsets = list(combinations(candidate_tuples, degree + 1))
            # shuffle subsets, so that false (chaff) points are not iterated one after another
            shuffle(subsets)
            if echo:
                print('Total of {} candidate minutiae and {} subsets found'.format(
                    len(candidate_tuples), len(subsets)
                ))
            # log total subsets
            log_dict['total_subsets'] = len(subsets)

            for i, subset in enumerate(subsets, 1):
                if echo:
                    print('Interpolating subset #{}...'.format(i))
                # use all points in subset execute polynomial interpolation
                # divide subset tuples to two list x and y again
                X, Y = list(zip(*subset))
                X = GaloisConverter.convert_int_list_to_gf_2_list(X, gf_exp)
                Y = GaloisConverter.convert_int_list_to_gf_2_list(Y, gf_exp)
                poly = self.extract_polynomial_gf_2(X, Y)
                if echo:
                    print('Interpolated secret polynomial is: {}'.format(poly))
                if PolynomialExtractor.check_crc_in_poly(poly, degree, crc_length, secret_length):
                    log_dict['evaluated_subsets'] = i
                    if echo:
                        print('Match found with subsets evaluated: {}'.format(i))
                    return True
                else:
                    if echo:
                        print('Unfortunately, failure in verifying CRC in above interpolated polynomial')
            if echo:
                print('Failure in all polynomial CRC verifications\n')
            log_dict['evaluated_subsets'] = -1
            return False

        def evaluate_random_subsets(candidate_tuples):
            """ Take random subsets on the fly and interpolate until max threshold reached """
            n = len(candidate_tuples)
            k = degree + 1
            try:
                max_threshold = factorial(n) // factorial(k) // factorial(n - k)
            except ValueError:
                max_threshold = 0

            log_dict['total_subsets'] = max_threshold

            for i in range(max_threshold):
                if echo:
                    print('Interpolating subset #{}...'.format(i))
                subset = sample(candidate_tuples, k)
                # use all points in subset execute polynomial interpolation
                # divide subset tuples to two list x and y again
                X, Y = list(zip(*subset))
                X = GaloisConverter.convert_int_list_to_gf_2_list(X, gf_exp)
                Y = GaloisConverter.convert_int_list_to_gf_2_list(Y, gf_exp)
                poly = self.extract_polynomial_gf_2(X, Y)
                if echo:
                    print('Interpolated secret polynomial is: {}'.format(poly))
                if PolynomialExtractor.check_crc_in_poly(poly, degree, crc_length, secret_length):
                    log_dict['evaluated_subsets'] = i
                    if echo:
                        print('Match found with subsets evaluated: {}'.format(i))
                    return True
                else:
                    if echo:
                        print('Unfortunately, failure in verifying CRC in above interpolated polynomial')
            if echo:
                print('Failure in all polynomial CRC verifications\n')
            log_dict['evaluated_subsets'] = -1
            return False

        gf_exp = self.gf_exp

        candidate_vault_tuples = set(zip(vault.vault_original_minutiae_rep, vault.vault_function_points_rep))
        if len(candidate_vault_tuples) > Constants.SUBSET_EVAL_THRES or Constants.RANDOM_SUBSET_EVAL:
            log_dict['subset_eval_random'] = True
            return evaluate_random_subsets(candidate_vault_tuples)
        else:
            log_dict['subset_eval_random'] = False
            return generate_all_subsets_version(candidate_vault_tuples)
