"""
    Transformer for geometric hashing
"""

import math
from Minutia import MinutiaNBIS_GH
from Minutia_Converter import MinutiaConverter


class GHTransformer:
    @staticmethod
    def generate_enrollment_table(vault_element_pairs):
        """
        generate geometric hashing table with vault element pairs
        converting the minutia representation to MinutiaNBIS_GH
        :param vault_element_pairs: list of VaultElements tuple: (minutia, poly mapping of minutia)
        :returns geometric hashing table as list of GHElementEnrollment
        """
        geom_table = []
        # list of MinutiaNBIS_GH
        minutiae_list = []
        function_points = []
        m_conv = MinutiaConverter()
        for element in vault_element_pairs:
            minutia_uint = element.x_rep
            minutia = m_conv.get_minutia_from_uint(minutia_uint)
            minutiae_list.append(MinutiaNBIS_GH.convert_from_MinutiaNBIS(minutia))
            function_points.append(element.y_rep)

        assert len(minutiae_list) == len(vault_element_pairs)
        for basis in minutiae_list:
            # Indices of minutiae_list in GHElementEnrollment is the same as vault_element_pairs
            geom_table.append(GHElementEnrollment(basis, minutiae_list, function_points))
        return geom_table

    @staticmethod
    def generate_verification_table_element(basis, minutiae_list):
        """
        generate verification table element from probe minutiae and basis
        :param basis: basis to transform probe minutiae to
        :param minutiae_list: list of minutiae (Minutia_NBIS_GH)
        :return: verification table element
        """
        return GHElementVerification(basis, minutiae_list)

    @staticmethod
    def convert_list_to_MinutiaNBIS_GH(minutiae_list):
        """
        converts list of MinutiaNBIS to MinutiaNBIS_GH
        :return: list of MinutiaNBIS_GH
        """
        result = []
        for minutia in minutiae_list:
            result.append(MinutiaNBIS_GH.convert_from_MinutiaNBIS(minutia))
        return result

    @staticmethod
    def transform_minutia_to_basis(m_basis: MinutiaNBIS_GH, m: MinutiaNBIS_GH):
        """
        transform one MinutiaNBIS_GH to new basis
        (caution: transformed minutia can be out of bounds of original minutia boundaries!)
        :param m_basis: Minutia used as basis as MinutiaNBIS_GH
        :param m: Minutia to be transformed as MinutiaNBIS_GH
        :return: transformed MinutiaNBIS_GH
        """
        x_diff = m.x - m_basis.x
        y_diff = m.y - m_basis.y
        cos_basis_theta = math.cos(math.radians(m_basis.theta))
        sin_basis_theta = math.sin(math.radians(m_basis.theta))
        x_transformed = int(round(x_diff * cos_basis_theta + y_diff * sin_basis_theta))
        y_transformed = int(round(-x_diff * sin_basis_theta + y_diff * cos_basis_theta))
        theta_diff = m.theta - m_basis.theta
        theta_transformed = theta_diff if theta_diff >= 0 else theta_diff + 360

        return MinutiaNBIS_GH(x_transformed, y_transformed, theta_transformed)

    @staticmethod
    def transform_minutiae_to_basis(basis, minutiae_list):
        """
        transforms all minutiae in list to basis
        :param basis: Minutia used as basis as MinutiaNBIS_GH
        :param minutiae_list: list of MinutiaNBIS_GH
        :return: list of transformed MinutiaNBIS_GH
        """
        transformed_minutiae_list = []
        for m in minutiae_list:
            transformed_minutiae_list.append(GHTransformer.transform_minutia_to_basis(basis, m))
        return transformed_minutiae_list


class GHElementEnrollment:
    """ Element of geometric hash table for enrollment using vault """
    def __init__(self, basis, minutiae_list, function_points, save_to_db=False):
        """
        :param basis: Minutia used as basis as MinutiaNBIS_GH
        :param minutiae_list: list of MinutiaNBIS_GH
        """
        self.basis = basis
        self.transformed_minutiae_list = GHTransformer.transform_minutiae_to_basis(self.basis, minutiae_list)

        if save_to_db:
            # representations to store in DB
            m_conv = MinutiaConverter()
            self.basis_rep = m_conv.get_uint_from_minutia(self.basis, non_negative=False)
            self.minutiae_rep = []
            for m in self.transformed_minutiae_list:
                self.minutiae_rep.append(m_conv.get_uint_from_minutia(m, non_negative=False))
            self.function_points_rep = function_points

    def __str__(self):
        return '(Basis:\n' \
            'x = {}\n' \
            'y = {}\n' \
            'theta = {}\n' \
            '#Minutiae:' \
            '{})'.format(self.basis.x, self.basis.y, self.basis.theta, len(self.transformed_minutiae_list))

    def __repr__(self):
        return '{}(Basis: ({}, {}, {}))'.format(
            self.__class__.__name__, self.basis.x, self.basis.y, self.basis.theta
        )


class GHElementVerification:
    """ Element of geometric hash table for verification using probe fingerprint """
    def __init__(self, basis, minutiae_list):
        """
        :param basis: Minutia used as basis as MinutiaNBIS_GH
        :param minutiae_list: list of MinutiaNBIS_GH
        """
        self.basis = basis
        self.transformed_minutiae_list = GHTransformer.transform_minutiae_to_basis(self.basis, minutiae_list)

    def __str__(self):
        return '(Basis:\n' \
               'x = {}\n' \
               'y = {}\n' \
               'theta = {}\n' \
               '#Minutiae:' \
               '{})'.format(self.basis.x, self.basis.y, self.basis.theta, len(self.transformed_minutiae_list))

    def __repr__(self):
        return '{}(Basis: ({}, {}, {}))'.format(
            self.__class__.__name__, self.basis.x, self.basis.y, self.basis.theta
        )
