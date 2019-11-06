"""
    Vault Extractor extracts minutiae from given vault and removes chaff points according to input minutiae set
"""

import random
import time

import Constants
from Geometric_Hashing_Transformer import GHTransformer
from Minutia import Minutia
from Minutia_Converter import MinutiaConverter
from Polynomial_Extractor import PolynomialExtractor
from Vault import Vault


class VaultVerifier:
    @staticmethod
    def unlock_vault_geom(vault: Vault, probe_minutiae, poly_degree, gf_exp, crc_length, secret_length, log_dict,
                          echo=False):
        """
        Given vault, find candidate minutiae according to probe minutiae (list of Minutia) using geometric hashing.
        Afterwards, run interpolation on candidate minutiae
        geom_table needs to exist in vault
        :returns True if match found in polynomial after interpolation, else False
        """

        def exit_false():
            """ :returns False for vault not unlocked """
            log_dict['amount_geom_table'] = len(vault_geom_table)
            log_dict['evaluated_subsets'] = -1
            log_dict['minutiae_candidates'] = 0
            log_dict['time_geom'] = time.time() - t_geom
            log_dict['geom_gallery_basis'] = None
            log_dict['geom_probe_basis'] = None
            vault.vault_original_minutiae_rep.clear()
            vault.vault_function_points_rep.clear()
            vault.vault_chaff_points_rep.clear()
            return False

        def get_geom_table_basis_threshold(probe_minutiae_gh):
            """
            Removes basis in geom_table of vault that correspond to no probe_minutiae orientation
            :param probe_minutiae_gh: list of probe minutiae as MinutiaNBIS_GH
            :return: changes vault.geom_table, no return value
            """
            geom_table = vault.geom_table.copy()
            for element_enroll in geom_table.copy():
                in_threshold = False
                for m in probe_minutiae_gh:
                    if abs(element_enroll.basis.theta - m.theta) <= Constants.BASIS_THETA_THRESHOLD:
                        # not removing element from geom_table
                        in_threshold = True
                        break
                # remove element from geom_table if there was no match
                if not in_threshold:
                    geom_table.remove(element_enroll)
            return geom_table

        assert vault.geom_table
        log_dict['thresholds'] = '({}/[{}/{}/{}/{}]/{})'.format(
            Constants.POINTS_DISTANCE,
            Constants.X_THRESHOLD, Constants.Y_THRESHOLD, Constants.THETA_THRESHOLD,
            Constants.TOTAL_THRESHOLD, Constants.BASIS_THETA_THRESHOLD)
        # start time geometric hashing
        t_geom = time.time()
        # create polynomial extractor
        poly_extractor = PolynomialExtractor(gf_exp)
        # convert probe minutia to GH form, iterate through probe_minutiae, taking random probe minutia as basis
        probe_minutiae_GH = GHTransformer.convert_list_to_MinutiaNBIS_GH(probe_minutiae)
        random.shuffle(probe_minutiae_GH)
        # remove all basis in geom_table that are not within threshold of probe_minutiae orientation
        vault_geom_table = get_geom_table_basis_threshold(probe_minutiae_GH)
        for cnt_basis, basis in enumerate(probe_minutiae_GH):
            # take random basis and try matching
            element_verification = GHTransformer.generate_verification_table_element(basis, probe_minutiae_GH.copy())
            for cnt_enroll, element_enrollment in enumerate(vault_geom_table):
                # check if basis in element_enrollment has similar orientation to current basis in probe
                if not (abs(element_verification.basis.theta - element_enrollment.basis.theta)
                        <= Constants.BASIS_THETA_THRESHOLD):
                    continue
                # clear lists in vault to be populated in decoding for each element in geom_table
                vault.vault_original_minutiae_rep.clear()
                vault.vault_function_points_rep.clear()
                vault.vault_chaff_points_rep.clear()
                assert len(element_enrollment.transformed_minutiae_list) == len(vault.vault_final_elements_pairs)
                # cnt_m_enr is representing the same indices also in vault_final_element_pairs
                match = 0
                candidates_verification = []
                candidates_enrollment = []
                candidate_minutiae_verification = element_verification.transformed_minutiae_list.copy()
                for cnt_m_enr, minutia_enrollment in enumerate(element_enrollment.transformed_minutiae_list):
                    if not candidate_minutiae_verification:
                        break
                    for minutia_verification in candidate_minutiae_verification:
                        if fuzzy_compare(minutia_enrollment, minutia_verification):
                            log_dict['geom_single_match'] += 1
                            # Only add element if not already in list
                            if not vault.vault_final_elements_pairs[
                                       cnt_m_enr].x_rep in vault.vault_original_minutiae_rep:
                                match += 1
                                # add representation (uint) to candidate minutiae
                                # first element corresponding to x value of vault tuple
                                vault.add_minutia_rep(vault.vault_final_elements_pairs[cnt_m_enr].x_rep)
                                # second element corresponding to y value of vault tuple
                                vault.add_function_point_rep(vault.vault_final_elements_pairs[cnt_m_enr].y_rep)
                                # candidate minutiae for logging purposes
                                candidates_verification.append(minutia_verification)
                                candidates_enrollment.append(minutia_enrollment)
                            assert match == len(vault.vault_original_minutiae_rep)
                        else:
                            # add to chaff points (but not relevant as minutia can not be matched in different basis)
                            chaff_candidate = vault.vault_final_elements_pairs[cnt_m_enr].x_rep
                            if chaff_candidate not in vault.vault_chaff_points_rep:
                                vault.add_chaff_point_rep(chaff_candidate)
                        log_dict['geom_iteration'] += 1

                if match >= Constants.MATCH_THRESHOLD:
                    assert match == len(vault.vault_original_minutiae_rep)
                    assert len(candidates_verification) == len(candidates_enrollment)
                    assert len(vault.vault_original_minutiae_rep) == len(vault.vault_function_points_rep)
                    assert len(vault.vault_function_points_rep) == len(candidates_enrollment)
                    # log iterations in geometric hashing, minutiae candidates. tries to interpolate and basis
                    log_dict['amount_geom_table'] += cnt_enroll
                    log_dict['minutiae_candidates'] = len(vault.vault_original_minutiae_rep)
                    log_dict['geom_match_tries'] += 1
                    log_dict['geom_gallery_basis'] = element_enrollment.basis
                    log_dict['geom_probe_basis'] = element_verification.basis

                    # time geometric hashing
                    log_dict['time_geom'] = time.time() - t_geom
                    # polynomial interpolation on candidate set function points and test CRC in extracted polynomials
                    t_interpol = time.time()
                    success = poly_extractor.interpolate_and_check_crc(vault, poly_degree, crc_length,
                                                                       secret_length, log_dict, echo=echo)
                    log_dict['time_interpolation'] += time.time() - t_interpol
                    if success:
                        # log candidate minutiae
                        if Constants.LOG_CANDIDATE_MINUTIAE:
                            log_candidates_minutia(Constants.LOG_CANDIDATES_PATH_PREFIX,
                                                   Constants.LOG_CANDIDATES_PATH_SUFFIX,
                                                   candidates_verification, candidates_enrollment,
                                                   element_verification.basis, element_enrollment.basis,
                                                   vault, number=log_dict['exp_number'])
                        return True

                # break if max threshold is reached
                if log_dict['geom_iteration'] > Constants.MAX_ITERATION_THRESHOLD:
                    print("Max iteration threshold reached!")
                    return exit_false()

        # unfortunately, no sets found
        return exit_false()


def minutia_in_probe(minutia, probe_minutiae):
    """ Tests if given minutia is existent in probe minutiae list
        :param probe_minutiae list of Minutia
        :param minutia Minutia
        :returns True if minutia in probe_minutiae with conditions of fuzzy_compare """
    for probe_minutia in probe_minutiae:
        if fuzzy_compare(minutia, probe_minutia):
            return True
    return False


def exact_compare(m1: Minutia, m2: Minutia):
    """ Compare two minutiae an exact way
        :returns True if m1 and m2 exactly the same else False """
    if m1.x == m2.x and m1.y == m2.y and m1.theta == m2.theta:
        return True
    else:
        return False


def fuzzy_compare(m1: Minutia, m2: Minutia):
    """ Compare two minutiae in a fuzzy way
        :returns True if m1 and m2 similar enough else False """

    def diff_in_threshold(m1: Minutia, m2: Minutia):
        """ Helper function to determine if x and y are in threshold (distance)
            The attributes of the minutia (x, y, theta) are compared if they are within threshold.
            Afterwards the sum of the differences is compared with a total threshold.
            :returns Boolean True if all """

        def in_threshold(x, y, threshold):
            if abs(x - y) <= threshold:
                return True
            else:
                return False

        def in_total_threshold(m1: Minutia, m2: Minutia):
            diff_total = abs(m1.x - m2.x) + abs(m1.y - m2.y) + abs(m1.theta - m2.theta)
            if diff_total <= Constants.TOTAL_THRESHOLD:
                return True
            else:
                return False

        if in_threshold(m1.x, m2.x, Constants.X_THRESHOLD) and \
                in_threshold(m1.y, m2.y, Constants.Y_THRESHOLD) and \
                in_threshold(m1.theta, m2.theta, Constants.THETA_THRESHOLD) and \
                in_total_threshold(m1, m2):
            return True
        else:
            return False

    return diff_in_threshold(m1, m2)


def log_minutia(log_path: str, minutia: Minutia, is_chaff_point: bool):
    """ logging minutia to file """
    with open(log_path, 'a') as file:
        if is_chaff_point:
            file.write('{} {} {} chaff_point\n'.format(minutia.x, minutia.y, minutia.theta))
        else:
            file.write('{} {} {} candidate_minutia\n'.format(minutia.x, minutia.y, minutia.theta))


def log_candidates_minutia_original(log_path: str, vault: Vault):
    m_conv = MinutiaConverter()
    # empty log file if it already exists
    open(log_path, 'w+').close()

    with open(log_path, 'a') as file:
        # write header
        file.write('x, y, theta, poly_map\n')
        assert len(vault.vault_original_minutiae_rep) == len(vault.vault_function_points_rep)
        for i, m_rep in enumerate(vault.vault_original_minutiae_rep):
            m = m_conv.get_minutia_from_uint(m_rep)
            file.write('{},{},{},{}\n'.format(
                m.x, m.y, m.theta, vault.vault_function_points_rep[i]
            ))


def log_candidates_minutia(log_path_prefix, log_path_suffix, candidates_verification, candidates_enrollment,
                           basis_ver, basis_enr, vault, number=0):
    """ Log converted candidate minutiae: in geometric hashing table (enrollment) vs probe minutiae (verification) """
    # empty log file if it already exists
    log_path = log_path_prefix + str(number) + log_path_suffix
    open(log_path, 'w+').close()

    with open(log_path, 'a') as file:
        # write header
        file.write('gallery x;'
                   'gallery y;'
                   'gallery theta;'
                   'probe x;'
                   'probe y;'
                   'probe theta;'
                   'vault x;'
                   'vault y\n')
        assert len(candidates_verification) == len(candidates_enrollment)
        for i, m_ver in enumerate(candidates_verification):
            m_enr = candidates_enrollment[i]
            vault_tuple_x = vault.vault_original_minutiae_rep[i]
            vault_tuple_y = vault.vault_function_points_rep[i]
            file.write('{};{};{};{};{};{};{};{}\n'.format(
                m_enr.x, m_enr.y, m_enr.theta, m_ver.x, m_ver.y, m_ver.theta, vault_tuple_x, vault_tuple_y
            ))
        file.write('{} b;{} b;{} b;{} b;{} b;{} b'.format(
            basis_enr.x, basis_enr.y, basis_enr.theta, basis_ver.x, basis_ver.y, basis_ver.theta
        ))


def log_basis_failure(geom_table, number=0):
    log_prefix = Constants.LOG_CANDIDATES_PATH_PREFIX + 'failure_'
    log_path = log_prefix + str(number) + Constants.LOG_CANDIDATES_PATH_SUFFIX
    open(log_path, 'w+').close()
    with open(log_path, 'a') as file:
        file.write('basis x;'
                   'basis y;'
                   'basis theta\n')
        for element_enroll in geom_table:
            file.write('{};{};{}\n'.format(element_enroll.basis.x, element_enroll.basis.y, element_enroll.basis.theta))
