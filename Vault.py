"""
    Vault as in fuzzy vault

    :var self.vault_original_minutiae: list of representation of minutiae without chaff points
    :var self.vault_chaff_points: list of representation of chaff points
"""

import random
from Polynomial_Generator import PolynomialGenerator
from Geometric_Hashing_Transformer import GHTransformer
from Constants import CHECK_CHAFF_POINT_MAPPING


class VaultElement:
    """ Element of a (fuzzy) Vault """
    def __init__(self, x_rep, y_rep):
        """
        :param x_rep 1st element of vault element tuple: e.g. representation of minutia
        :param y_rep 2nd element of vault element tuple: e.g. polynomial evaluated at minutia_rep """
        self.x_rep = x_rep
        self.y_rep = y_rep

    def __str__(self):
        return '({}, {})\n'.format(self.x_rep, self.y_rep)

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__, self.x_rep, self.y_rep
        )


class Vault:
    def __init__(self):
        # list of vault elements (tuples)
        self.vault_final_elements_pairs = []
        # used in encoding and decoding. while decoding original_minutiae are candidate_minutiae
        self.vault_original_minutiae_rep = []
        # only used in encoding
        self.vault_chaff_points_rep = []
        # used for decoding vault. all points that correspond to original_minutiae_rep are stored here
        self.vault_function_points_rep = []
        # table for geometric hashing
        self.geom_table = []
        self.clear_vault()

    def add_minutia_rep(self, minutia_rep):
        """ Add minutia to vault
            :param minutia_rep is a uint representation of a minutia """
        self.vault_original_minutiae_rep.append(minutia_rep)

    def add_chaff_point_rep(self, chaff_point_rep):
        """ Add chaff point to vault
            :param chaff_point_rep is a uint representation of a generated minutia """
        self.vault_chaff_points_rep.append(chaff_point_rep)

    def add_vault_element(self, vault_element: VaultElement):
        self.vault_final_elements_pairs.append(vault_element)

    def add_function_point_rep(self, function_point_rep):
        """ Add function point that corresponds to a original_minutiae_rep to vault_function_points for decoding
            :param function_point_rep is a uint representation of a polynomial mapping minutia """
        self.vault_function_points_rep.append(function_point_rep)

    def clear_vault(self):
        """ Clear all lists in vault """
        self.vault_final_elements_pairs.clear()
        self.vault_original_minutiae_rep.clear()
        self.vault_chaff_points_rep.clear()
        self.vault_function_points_rep.clear()
        self.geom_table.clear()

    def evaluate_polynomial_on_minutiae(self, poly_generator: PolynomialGenerator, echo=False):
        """ Evaluate polynomial on original minutiae in vault_minutiae and save to vault_elements_pairs
            :param poly_generator: generator containing polynomial"""
        for minutia_rep in self.vault_original_minutiae_rep:
            vault_element = VaultElement(minutia_rep, poly_generator.evaluate_polynomial_gf_2(minutia_rep))
            self.add_vault_element(vault_element)
            if echo:
                print("...", end="")
        if echo:
            print("\nFinish evaluating polynomial of vault elements")

    def evaluate_random_on_chaff_points(self, poly_generator: PolynomialGenerator, m):
        """ Generate random evaluation of chaff points for second element of VaultElement (X,Y)
            Random points Y do not lie on polynomial(X) = Y
            :param poly_generator: generator containing polynomial
            :param m describes largest number exponential 2**m """
        # gets vault elements from original minutiae to generate similar values
        min_digits = 9
        max_digits = 10
        max_number = 2 ** m
        if self.vault_final_elements_pairs:
            digits_list = []
            for element in self.vault_final_elements_pairs:
                digits_list.append(len(str(element.y_rep)))
            min_digits = int(min(digits_list))
            max_digits = int(max(digits_list))

        # generate random Y and check if Y = polynomial(X) where X = chaff_point
        for chaff_point in self.vault_chaff_points_rep:
            y_candidate = 0

            # check for on_polynomial normally omitted due to performance reasons
            if CHECK_CHAFF_POINT_MAPPING:
                y_real = poly_generator.evaluate_polynomial_gf_2(chaff_point)
                on_polynomial = True
            else:
                y_real = 0
                on_polynomial = False

            while on_polynomial or y_candidate > max_number or y_candidate == 0:
                y_candidate = self.random_int_digits(min_digits, max_digits)
                if y_real != y_candidate:
                    on_polynomial = False
            self.add_vault_element(VaultElement(chaff_point, y_candidate))

    def finalize_vault(self):
        """ Delete vault_original_minutiae and vault_chaff_points, scramble vault_final_elements_pairs"""
        self.vault_original_minutiae_rep.clear()
        self.vault_chaff_points_rep.clear()
        random.shuffle(self.vault_final_elements_pairs)

    def random_int_digits(self, min_digits, max_digits):
        """ Helper function to generate random integer between min_digits and max_digits
            Example: :param min_digits = 3, max_digits = 5: random integer between 100 and 99999 """
        range_start = 10 ** (min_digits - 1)
        range_end = (10 ** max_digits) - 1
        return random.randint(range_start, range_end)

    def get_smallest_original_minutia(self):
        """ Get smallest original minutia for better chaff points creation
            :returns smallest original minutia in uint """
        return min(self.vault_original_minutiae_rep)

    def create_geom_table(self):
        self.geom_table = GHTransformer.generate_enrollment_table(self.vault_final_elements_pairs)
