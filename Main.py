import random
import time
import datetime
import os
import sys
import copy
from itertools import combinations
from shutil import copyfile

from Chaff_Points_Generator import ChaffPointsGenerator
from Constants import XYT_GALLERY, XYT_PROBE, DATABASE_2B_PATH, \
    GF_2_M, CRC_LENGTH, POINTS_DISTANCE, \
    SAVE_VAULT_TO_DB, GET_VAULT_FROM_DB, FINGER_END, FINGER_START, CAPTURE_END, CAPTURE_START, \
    DATABASE_2A_FLAG, DATABASE_2A_PATH, SPLIT_COMPUTATION, ONE_TO_ONE_FVC_PROTOCOL
import Constants
from Minutia_Converter import MinutiaConverter
from Minutiae_Extractor import MinutiaeExtractor
from Polynomial_Generator import PolynomialGenerator
from Vault import Vault
from Vault_Verifier import VaultVerifier
from DBHandler import DBHandler


def main():
    """
    Run algorithm according to command line input arguments
    1st parameter:
        - 0: run whole database
        - x: where x > 0, run that many iterations of main algorithm
    """
    if not len(sys.argv) == 2:
        print("False amount of arguments detected. Please provide ONE running parameter as integer.")
        exit(-1)

    # get argument from command line
    try:
        iteration = int(sys.argv[1])
    except ValueError:
        print("Please provide an integer as argument")
        iteration = -1
        exit(-1)

    assert iteration >= 0

    if DATABASE_2A_FLAG:
        database_path = DATABASE_2A_PATH
    else:
        database_path = DATABASE_2B_PATH

    if iteration == 0:
        # run whole database
        for _ in range(1, Constants.RUN_DB_ITERATIONS + 1):
            run_over_database(database_path, echo=False)
            change_parameters()
    else:
        # clear log file and add log header
        log_parameter_file = Constants.LOG_FILE_PARAMETER_TESTING
        initialize_parameter_testing_log(log_parameter_file)

        # loop for parameter experimentation, run amount of iterations specified by argument
        cnt = 1
        while cnt <= iteration:
            log_parameter_file = Constants.LOG_FILE_PARAMETER_TESTING
            run_experiment_single(database_path, log_parameter_file, None,
                                  XYT_GALLERY, XYT_PROBE, log_flag=Constants.LOG_VAULT_MINUTIAE, echo=True, number=cnt)
            cnt += 1
    notify_finish()


def change_parameters():

    def update_log_file_names():
        """ Initiate all log files names according to other constants and datetime """
        now = datetime.datetime.now()
        date_time_now_str = '{}_{}'.format(now.strftime("%Y%m%d"), now.strftime("%H%M"))

        # Logging parameter testing and database testing
        Constants.LOG_PARAM = 'param_poly{}_minu{}_{}.csv'.format(
            Constants.POLY_DEGREE, Constants.MINUTIAE_POINTS_AMOUNT, date_time_now_str)
        Constants.LOG_DB = 'db_poly{}_minu{}_{}.csv'.format(
            Constants.POLY_DEGREE, Constants.MINUTIAE_POINTS_AMOUNT, date_time_now_str)
        Constants.LOG_FILE_PARAMETER_TESTING = 'out/' + Constants.LOG_PARAM
        Constants.LOG_FILE_DATABASE_TESTING = 'out/' + Constants.LOG_DB

        # Logging in Vault_Verifier
        Constants.LOG_PATH = 'out/vault_minutiae_{}.log'.format(date_time_now_str)
        Constants.LOG_CANDIDATES_PATH_PREFIX = 'out/candidate_minutiae_{}_'.format(date_time_now_str)

        # Log summary
        Constants.LOG_SUMMARY_PATH = Constants.DB_TESTING_FOLDER + 'test_summary_all_{}.csv'.format(date_time_now_str)
        Constants.LOG_SUMMARY_2A_PATH = Constants.DB_2A_FOLDER + 'test_summary_all_{}.csv'.format(date_time_now_str)
        Constants.LOG_TOTAL_DB_2A_PATH = Constants.DB_2A_FOLDER + 'db_poly{}_minu{}_{}.csv'.format(
            Constants.POLY_DEGREE, Constants.MINUTIAE_POINTS_AMOUNT, date_time_now_str)
        Constants.LOG_TOTAL_PARAM_2A_PATH = Constants.DB_2A_FOLDER + 'param_poly{}_minu{}_{}.csv'.format(
            Constants.POLY_DEGREE, Constants.MINUTIAE_POINTS_AMOUNT, date_time_now_str)

    Constants.POLY_DEGREE = Constants.POLY_DEGREE + Constants.CHANGE_POLY
    Constants.CHAFF_POINTS_AMOUNT = Constants.CHAFF_POINTS_AMOUNT + Constants.CHANGE_CHAFF_POINTS
    Constants.MINUTIAE_POINTS_AMOUNT = Constants.MINUTIAE_POINTS_AMOUNT + Constants.CHANGE_MINU_POINTS

    Constants.POINTS_DISTANCE = Constants.POINTS_DISTANCE + Constants.CHANGE_POINTS_DIST

    Constants.X_THRESHOLD = Constants.X_THRESHOLD + Constants.CHANGE_X_THRES
    Constants.Y_THRESHOLD = Constants.Y_THRESHOLD + Constants.CHANGE_Y_THRES
    Constants.THETA_THRESHOLD = Constants.THETA_THRESHOLD + Constants.CHANGE_THETA_THRES
    Constants.TOTAL_THRESHOLD = Constants.TOTAL_THRESHOLD + Constants.CHANGE_TOT_THRES

    Constants.BASIS_THETA_THRESHOLD = Constants.BASIS_THETA_THRESHOLD + Constants.CHANGE_BASIS_THETA
    # update log_files with new parameters
    update_log_file_names()


def run_over_database(database_path, echo=True):
    """
    Run experiment over whole database
    :param database_path: path to folder of fingerprint templates
    :param echo: print intermediate messages to console
    """

    def initiate_db_testing_log(log_file):
        """ clear log file and add log header for logging database matching results """
        if not os.path.exists('out'):
            os.makedirs('out')
        open(log_file, 'w+').close()
        with open(log_file, 'a') as log:
            log.write('gallery; capture; probe; capture; match\n')

    # list all .xyt files in database
    all_paths = os.listdir(database_path)
    all_paths.sort()
    all_xyt = []
    for path in all_paths:
        if path.endswith(".xyt"):
            all_xyt.append(path)

    if ONE_TO_ONE_FVC_PROTOCOL:
        # Create log file and initiate logs for 1vs1 and FVC protocol
        prefix_one = '1_vs_1_'
        prefix_fvc = 'fvc_'
        out_folder = 'out/'

        log_one_param = out_folder + prefix_one + Constants.LOG_PARAM
        log_one_db = out_folder + prefix_one + Constants.LOG_DB
        log_fvc_param = out_folder + prefix_fvc + Constants.LOG_PARAM
        log_fvc_db = out_folder + prefix_fvc + Constants.LOG_DB

        initialize_parameter_testing_log(log_one_param)
        initiate_db_testing_log(log_one_db)
        initialize_parameter_testing_log(log_fvc_param)
        initiate_db_testing_log(log_fvc_db)

        # FVC protocol or 1 vs 1: FMR
        # all_xyt_one contains all capture 1 of all fingers
        all_xyt_one = []
        for path in all_xyt:
            if path.endswith('_1.xyt'):
                all_xyt_one.append(path)
        assert len(all_xyt_one) == 140
        combinations_fmr_finger = combinations(all_xyt_one, 2)
        for gallery_xyt, probe_xyt in combinations_fmr_finger:
            run_experiment_single(database_path, log_fvc_param, log_fvc_db,
                                  gallery_xyt, probe_xyt, echo=echo)
        # 1vs1 protocol copy FMR
        open(log_one_param, 'w+').close()
        open(log_one_db, 'w+').close()
        copyfile(log_fvc_param, log_one_param)
        copyfile(log_fvc_db, log_one_db)

        # 1vs1 protocol: FNMR
        for finger in range(1, 141):
            run_experiment_single(database_path, log_one_param, log_one_db,
                                  '{}_1.xyt'.format(finger), '{}_2.xyt'.format(finger), echo=echo)
        # FVC protocol: FNMR
        for finger in range(1, 141):
            # for one finger:
            # all_xyt_finger contains all captures of 'finger'
            all_xyt_finger = []
            for path in all_xyt:
                if path.startswith(str(finger) + '_'):
                    all_xyt_finger.append(path)
            assert len(all_xyt_finger) == 12
            combinations_fnmr_finger = combinations(all_xyt_finger, 2)
            for gallery_xyt, probe_xyt in combinations_fnmr_finger:
                run_experiment_single(database_path, log_fvc_param, log_fvc_db,
                                      gallery_xyt, probe_xyt, echo=echo)
    else:
        # run through whole database
        if SPLIT_COMPUTATION:
            # initiate logs for split computation
            log_parameter_file = Constants.LOG_FILE_PARAMETER_2A
            log_db_file = Constants.LOG_FILE_DATABASE_2A
            initialize_parameter_testing_log(log_parameter_file)
            initiate_db_testing_log(log_db_file)

            # Run through whole DB with splitting on machines
            for finger in range(FINGER_START, FINGER_END):
                for capture in range(CAPTURE_START, CAPTURE_END):
                    if Constants.REUSE_VAULT:
                        run_experiment_reuse_vault('{}_{}.xyt'.format(finger, capture), all_xyt, database_path,
                                                   log_parameter_file, log_db_file, echo=echo)
                    else:
                        for probe_xyt in all_xyt:
                            run_experiment_single(database_path, log_parameter_file, log_db_file,
                                                  '{}_{}.xyt'.format(finger, capture), probe_xyt, echo=echo)
        else:
            # initiate logs normally
            log_parameter_file = Constants.LOG_FILE_PARAMETER_TESTING
            log_db_file = Constants.LOG_FILE_DATABASE_TESTING
            initialize_parameter_testing_log(log_parameter_file)
            initiate_db_testing_log(log_db_file)

            # loop through whole database (folder)
            for gallery_xyt in all_xyt:
                if Constants.REUSE_VAULT:
                    run_experiment_reuse_vault(gallery_xyt, all_xyt, database_path, log_parameter_file, log_db_file,
                                               echo=echo)
                else:
                    for probe_xyt in all_xyt:
                        run_experiment_single(database_path, log_parameter_file, log_db_file, gallery_xyt, probe_xyt,
                                              echo=echo)


def run_experiment_single(db_path, log_parameter_file, log_db_file, gallery_xyt, probe_xyt,
                          log_flag=True, echo=False, number=0):
    """
    Run experiment and match gallery with probe xyt once
    :param db_path: path where xyt paths are stored
    :param log_parameter_file: name of log file to save parameters
    :param log_db_file: name of log file to save db results
    :param gallery_xyt: name of gallery xyt file
    :param probe_xyt: name of probe xyt file
    :param log_flag: log functionality
    :param echo: if True, printing intermediate messages to console
    :param number: experiment run number
    :param number: number of experiment
    :returns: True if match is found (gallery is same finger as probe)
    """

    def log_parameters():
        too_few_minutia = False
        with open(log_parameter_file, 'a') as log:
            versus = '{} vs {}'.format(probe_xyt, gallery_xyt)
            minutiae_candidates = log_dict['minutiae_candidates']
            total_subsets = log_dict['total_subsets']
            evaluated_subsets = log_dict['evaluated_subsets']
            amount_geom = log_dict['amount_geom_table']
            t_geom_creation = log_dict['geom_creation_time']
            t_interpol = log_dict['time_interpolation']
            t_geom = log_dict['time_geom']
            tries_geom = log_dict['geom_match_tries']
            single_matches_geom = log_dict['geom_single_match']
            geom_iteration = log_dict['geom_iteration']
            if log_dict['too_few_minutiae_gallery']:
                too_few_minutia = True
                gallery_basis_str = 'Invalid'
                probe_basis_str = 'No Basis'
            elif log_dict['too_few_minutiae_probe']:
                too_few_minutia = True
                gallery_basis_str = 'No Basis'
                probe_basis_str = 'Invalid'
            else:
                gallery_basis_str = print_minutia_basis(log_dict['geom_gallery_basis'])
                probe_basis_str = print_minutia_basis(log_dict['geom_probe_basis'])
            thresholds = log_dict['thresholds']
            t_encode = round(t_middle - t_start, 2) if not too_few_minutia else 0
            t_decode = round(t_end - t_middle, 2) if not too_few_minutia else 0
            t_total = round(t_end - t_start, 2) if not too_few_minutia else 0
            subset_eval = 'Subsets random' if log_dict['subset_eval_random'] else 'Subsets precomputed'
            log.write('{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n'.format(
                versus, Constants.POLY_DEGREE, Constants.MINUTIAE_POINTS_AMOUNT, Constants.CHAFF_POINTS_AMOUNT,
                thresholds,
                secret_length + CRC_LENGTH, minutiae_candidates, total_subsets, evaluated_subsets,
                t_encode, t_decode, round(t_geom_creation, 2),
                round(t_interpol, 2), round(t_geom, 2), t_total, tries_geom, single_matches_geom,
                amount_geom, geom_iteration, gallery_basis_str, probe_basis_str, subset_eval
            ))

    def log_database_matches(match):
        # log result
        with open(log_db_file, 'a') as log_db:
            gallery_str = gallery_xyt.replace('.xyt', '')
            probe_str = probe_xyt.replace('.xyt', '')
            gallery_finger, gallery_capture = gallery_str.split('_')
            probe_finger, probe_capture = probe_str.split('_')
            if match:
                match_str = "wahr"
            else:
                match_str = "falsch"
            if log_dict['too_few_minutiae_gallery']:
                match_str = "invalid gallery"
            if log_dict['too_few_minutiae_probe']:
                match_str = "invalid probe"
            log_db.write('{g_f};{g_c};{p_f};{p_c};{match_str}\n'.format(
                g_f=gallery_finger, g_c=gallery_capture, p_f=probe_finger, p_c=probe_capture, match_str=match_str))

    if echo:
        print('==========================================================')
        print('Run {xyt_g} vs {xyt_p}'.format(xyt_g=gallery_xyt, xyt_p=probe_xyt))
        print('==========================================================')

    # time execution
    t_start = time.time()

    # create DB handler
    db_handler = DBHandler()
    # create dict for logging purposes and initiate all default values
    log_dict = dict()
    initialize_log_dict(log_dict, number=number)

    # calculate secret according to polynomial degree. secret has to be able to be encoded in bytes (*8)
    secret_bytes = generate_smallest_secret(Constants.POLY_DEGREE, CRC_LENGTH, min_size=128, echo=echo)
    secret_length = len(secret_bytes) * 8

    fuzzy_vault = generate_vault(db_path + gallery_xyt, Constants.MINUTIAE_POINTS_AMOUNT, Constants.CHAFF_POINTS_AMOUNT,
                                 Constants.POLY_DEGREE, secret_bytes, CRC_LENGTH, GF_2_M, log_dict, echo=echo)
    if not fuzzy_vault:
        if echo:
            print('Failure due to too few minutiae to generate vault...\n')
        log_dict['too_few_minutiae_gallery'] = True
        if log_flag:
            log_parameters()
            if log_db_file:
                log_database_matches(False)
        return

    if echo:
        print('Finished generating fuzzy vault')

    # generate random vault id
    vault_id = random.randint(1, 100)

    # send vault to database
    if SAVE_VAULT_TO_DB:
        store_in_cosmos_db(db_handler, fuzzy_vault, vault_id)

    # end of ENCODE and start of DECODE
    t_middle = time.time()

    t_start_geom_creation = time.time()
    # get vault from database
    if GET_VAULT_FROM_DB:
        db_vault = retrieve_from_cosmos_db(db_handler, vault_id)
        db_vault.create_geom_table()
        log_dict['geom_creation_time'] = round(time.time() - t_start_geom_creation, 2)
        success = verify_secret(db_path + probe_xyt, Constants.MINUTIAE_POINTS_AMOUNT, Constants.POLY_DEGREE,
                                CRC_LENGTH, secret_length, GF_2_M, db_vault, log_dict, echo=echo)
        db_vault.clear_vault()
    else:
        fuzzy_vault.create_geom_table()
        log_dict['geom_creation_time'] = round(time.time() - t_start_geom_creation, 2)
        success = verify_secret(db_path + probe_xyt, Constants.MINUTIAE_POINTS_AMOUNT, Constants.POLY_DEGREE,
                                CRC_LENGTH, secret_length, GF_2_M, fuzzy_vault, log_dict, echo=echo)
        fuzzy_vault.clear_vault()

    # finish time execution
    t_end = time.time()

    # log run
    if log_flag:
        log_parameters()
        if log_db_file:
            log_database_matches(success)

    # clear up
    log_dict.clear()
    db_handler.close_handler()

    if echo:
        print('Execution time: {} seconds'.format(int(t_end - t_start)))

        # prints SUCCESS or FAILURE
        if success:
            print("SUCCESS\n")
        else:
            print("FAILURE...\n")


def run_experiment_reuse_vault(gallery_xyt, probe_xyts, db_path, log_parameter_file, log_db_file, echo=False):
    """
    Run experiments with fuzzy vault created from gallery_xyt and match with all probe_xyts
    Detailed print statements are turned off
    """

    def log_parameters(probe_xyt_to_log, time_encode, time_decode):
        with open(log_parameter_file, 'a') as log:
            versus = '{} vs {}'.format(probe_xyt_to_log, gallery_xyt)
            minutiae_candidates = log_dict['minutiae_candidates']
            total_subsets = log_dict['total_subsets']
            evaluated_subsets = log_dict['evaluated_subsets']
            amount_geom = log_dict['amount_geom_table']
            t_geom_creation = log_dict['geom_creation_time']
            t_interpol = log_dict['time_interpolation']
            t_geom = log_dict['time_geom']
            tries_geom = log_dict['geom_match_tries']
            single_matches_geom = log_dict['geom_single_match']
            geom_iteration = log_dict['geom_iteration']
            if log_dict['too_few_minutiae_gallery']:
                gallery_basis_str = 'Invalid'
                probe_basis_str = 'No Basis'
            elif log_dict['too_few_minutiae_probe']:
                gallery_basis_str = 'No Basis'
                probe_basis_str = 'Invalid'
            else:
                gallery_basis_str = print_minutia_basis(log_dict['geom_gallery_basis'])
                probe_basis_str = print_minutia_basis(log_dict['geom_probe_basis'])
            thresholds = log_dict['thresholds']
            time_encode_str = round(time_encode, 2)
            time_decode_str = round(time_decode, 2)
            time_total_str = round(time_encode + time_decode, 2)
            subset_eval = 'Subsets random' if log_dict['subset_eval_random'] else 'Subsets precomputed'
            log.write('{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n'.format(
                versus, Constants.POLY_DEGREE, Constants.MINUTIAE_POINTS_AMOUNT, Constants.CHAFF_POINTS_AMOUNT,
                thresholds,
                secret_length + CRC_LENGTH, minutiae_candidates, total_subsets, evaluated_subsets,
                time_encode_str, time_decode_str, round(t_geom_creation, 2),
                round(t_interpol, 2), round(t_geom, 2), time_total_str, tries_geom, single_matches_geom,
                amount_geom, geom_iteration, gallery_basis_str, probe_basis_str, subset_eval
            ))

    def log_database_matches(probe_xyt_to_log, match, log_dictionary):
        with open(log_db_file, 'a') as log_db:
            gallery_str = gallery_xyt.replace('.xyt', '')
            probe_str = probe_xyt_to_log.replace('.xyt', '')
            gallery_finger, gallery_capture = gallery_str.split('_')
            probe_finger, probe_capture = probe_str.split('_')
            if match:
                match_str = "wahr"
            else:
                match_str = "falsch"
            if log_dictionary['too_few_minutiae_gallery']:
                match_str = "invalid gallery"
            if log_dictionary['too_few_minutiae_probe']:
                match_str = "invalid probe"
            log_db.write('{g_f};{g_c};{p_f};{p_c};{match_str}\n'.format(
                g_f=gallery_finger, g_c=gallery_capture, p_f=probe_finger, p_c=probe_capture, match_str=match_str))

    # ENCODE fuzzy vault
    # time execution
    t_encode_start = time.time()

    # create dict for logging purposes and initiate all default values
    log_dict = dict()
    initialize_log_dict(log_dict)

    # calculate secret according to polynomial degree. secret has to be able to be encoded in bytes (*8)
    secret_bytes = generate_smallest_secret(Constants.POLY_DEGREE, CRC_LENGTH, min_size=128, echo=False)
    secret_length = len(secret_bytes) * 8

    fuzzy_vault = generate_vault(db_path + gallery_xyt, Constants.MINUTIAE_POINTS_AMOUNT,
                                 Constants.CHAFF_POINTS_AMOUNT,
                                 Constants.POLY_DEGREE, secret_bytes, CRC_LENGTH, GF_2_M, log_dict, echo=False)
    if not fuzzy_vault:
        if echo:
            print('Failure due to too few minutiae to generate vault...\n')
        log_dict['too_few_minutiae_gallery'] = True
        for probe_xyt in probe_xyts:
            log_parameters(probe_xyt + ' invalid gallery', 0, 0)
            log_database_matches(probe_xyt, False, log_dict)
        return

    t_start_geom_creation = time.time()
    fuzzy_vault.create_geom_table()
    log_dict['geom_creation_time'] = round(time.time() - t_start_geom_creation, 2)

    # end of ENCODE and start of DECODE
    t_encode_end = time.time()
    t_encode = t_encode_end - t_encode_start

    if echo:
        print('**********************************************************')
        print('Created fuzzy vault with {xyt_g}'.format(xyt_g=gallery_xyt))
        print('**********************************************************')

    # DECODE fuzzy vault
    # loop over probe_xyt and try to unlock vault from gallery_xyt
    for probe_xyt in probe_xyts:
        if echo:
            print('==========================================================')
            print('Run {xyt_g} vs {xyt_p}'.format(xyt_g=gallery_xyt, xyt_p=probe_xyt))
            print('==========================================================')

        initialize_log_dict(log_dict)

        # copy fuzzy vault for decoding
        fuzzy_vault_clone = copy.deepcopy(fuzzy_vault)

        # decoding
        t_decode_start = time.time()
        success = verify_secret(db_path + probe_xyt, Constants.MINUTIAE_POINTS_AMOUNT, Constants.POLY_DEGREE,
                                CRC_LENGTH, secret_length, GF_2_M, fuzzy_vault_clone, log_dict, echo=False)
        fuzzy_vault_clone.clear_vault()

        # finish time execution
        t_decode_end = time.time()
        t_decode = t_decode_end - t_decode_start

        # log run
        log_parameters(probe_xyt, t_encode, t_decode)
        log_database_matches(probe_xyt, success, log_dict)

        # clear up
        log_dict.clear()

        # prints SUCCESS or FAILURE
        if echo:
            print('Execution time: {} seconds'.format(int(t_encode + t_decode)))
            if success:
                print("SUCCESS\n")
            else:
                print("FAILURE...\n")


def generate_vault(xyt_input_path, minutiae_points_amount, chaff_points_amount, poly_degree, secret, crc_length,
                   gf_exp, log_dict, echo=False):
    # extract minutiae from template
    nbis_minutiae_extractor = MinutiaeExtractor()
    minutiae_list = nbis_minutiae_extractor.extract_minutiae_from_xyt(xyt_input_path)
    if len(minutiae_list) < minutiae_points_amount:
        if echo:
            print('Not enough minutiae in template to proceed for generation of vault...')
        log_dict['too_few_minutiae_gallery'] = True
        return None

    vault = Vault()
    m2b = MinutiaConverter()

    # Cut low quality minutiae and convert all minutiae to uint and add to vault
    genuine_minutiae_list = []
    for candidate in minutiae_list:
        if len(genuine_minutiae_list) == minutiae_points_amount:
            break
        too_close = False
        for minutia in genuine_minutiae_list:
            if candidate.distance_to(minutia) <= POINTS_DISTANCE:
                too_close = True
                break
        if not too_close:
            genuine_minutiae_list.append(candidate)

    for minutia in genuine_minutiae_list:
        vault.add_minutia_rep(m2b.get_uint_from_minutia(minutia))

    # create chaff points and add to vault
    chaff_points_list = ChaffPointsGenerator.generate_chaff_points_randomly(chaff_points_amount, genuine_minutiae_list,
                                                                            vault.get_smallest_original_minutia(), m2b)
    for chaff_point in chaff_points_list:
        vault.add_chaff_point_rep(m2b.get_uint_from_minutia(chaff_point))

    # generate secret polynomial
    secret_poly_generator = PolynomialGenerator(secret, poly_degree, crc_length, gf_exp)
    if echo:
        print('Coefficients of secret polynomial: {}'.format(secret_poly_generator.coefficients))

    # evaluate polynomial at all vault minutiae points (not at chaff points)
    vault.evaluate_polynomial_on_minutiae(secret_poly_generator, echo=echo)

    # generate random evaluation for chaff points
    vault.evaluate_random_on_chaff_points(secret_poly_generator, gf_exp)

    # finalize vault (delete information on vault creation except vault_final_elements_pairs)
    vault.finalize_vault()

    return vault


def verify_secret(xyt_input_path, minutiae_points_amount, poly_degree, crc_length, secret_length, gf_exp, vault: Vault,
                  log_dict, echo=False):
    """
    :returns: True if match is found, False otherwise
    """
    # extract minutiae from template
    nbis_minutiae_extractor = MinutiaeExtractor()
    minutiae_list = nbis_minutiae_extractor.extract_minutiae_from_xyt(xyt_input_path)
    if len(minutiae_list) < minutiae_points_amount:
        if echo:
            print('Not enough minutiae in template to proceed for extraction of secret...')
        log_dict['too_few_minutiae_probe'] = True
        return False

    # extract and restore minutiae from vault using minutiae list from probe, only good quality points taken
    return VaultVerifier.unlock_vault_geom(vault, minutiae_list[0:minutiae_points_amount], poly_degree, gf_exp,
                                           crc_length, secret_length, log_dict, echo=echo)


def store_in_cosmos_db(db_handler, vault, vault_id):
    """
    Store vault at CosmosDB defined in db_handler
    :param db_handler: handler for CosmosDB
    :param vault: vault to be stored
    :param vault_id: vault id to which vault is stored at DB
    """
    # send vault to database
    db_handler.insert_fuzzy_vault(vault, vault_id)


def retrieve_from_cosmos_db(db_handler, vault_id):
    """
    Retrieve vault from CosmosDB defined in db_handler
    :param db_handler: handler for CosmosDB
    :param vault_id: vault ID to be retrieved
    :return: Vault
    """
    vault_ret = db_handler.find_fuzzy_vault(vault_id)
    return vault_ret


def generate_smallest_secret(poly_degree, crc_length, min_size=0, echo=False):
    """ Helper function to generate smallest secret which is:
        - divisible by 8, so that it can be encoded to bytes
        - secret length + crc_length is divisible by poly_degree + 1
            to be able to split secret into coefficients for polynomial
        :param poly_degree: polynomial degree as int
        :param crc_length: CRC length as int
        :param min_size: minimum bit size as int
        :param echo: if True, printing intermediate messages to console
        :returns bytes """

    if min_size % 8 == 0:
        candidate_size = min_size
    else:
        candidate_size = min_size + (8 - (min_size % 8))
    assert candidate_size % 8 == 0
    while not ((candidate_size + crc_length) % (poly_degree + 1) == 0):
        candidate_size += 8
    # generate random secret
    secret_int = random.randint(0, 2 ** candidate_size - 1)
    assert candidate_size % 8 == 0
    secret_bytes = secret_int.to_bytes(candidate_size // 8, byteorder='big')
    if echo:
        print('Secret size is {} bits'.format(candidate_size))
        print('Secret bytes are {}'.format(secret_bytes))
    return secret_bytes


def initialize_log_dict(log_dict, number=0):
    # experiment number
    log_dict['exp_number'] = number
    # how many elements iterated through in geometric table
    log_dict['amount_geom_table'] = 0
    # number of subsets total
    log_dict['total_subsets'] = 0
    # how many subsets evaluated in polynomial interpolation
    log_dict['evaluated_subsets'] = -1
    # how many minutiae candidates before polynomial interpolation
    log_dict['minutiae_candidates'] = 0
    # time of creation of geometric hashing table
    log_dict['geom_creation_time'] = 0
    # time of polynomial interpolation (only the last try)
    log_dict['time_interpolation'] = 0
    # total time of geometric hashing (all iterations)
    log_dict['time_geom'] = 0
    # how many times candidate sets have been discovered in geometric hashing
    log_dict['geom_match_tries'] = 0
    # how many total iterations have been computed in geometric hashing (each subloop)
    log_dict['geom_iteration'] = 0
    # how many single minutiae matches have been found in geometric hashing
    log_dict['geom_single_match'] = 0
    # basis selected in gallery for geometric hashing in geom table for matching and interpolation
    log_dict['geom_gallery_basis'] = None
    # basis selected in probe for geometric hashing in geom table for matching and interpolation
    log_dict['geom_probe_basis'] = None
    # thresholds in Vault_Verifier
    log_dict['thresholds'] = ''
    # flag if probe or gallery fingerprint template has too few minutiae
    log_dict['too_few_minutiae_probe'] = False
    log_dict['too_few_minutiae_gallery'] = False
    # log if choice of candidate subsets is done randomly
    log_dict['subset_eval_random'] = Constants.RANDOM_SUBSET_EVAL


def initialize_parameter_testing_log(log_parameter_file):
    """ clear log file and add log header for logging parameter testing """
    if not os.path.exists('out'):
        os.makedirs('out')
    open(log_parameter_file, 'w+').close()
    with open(log_parameter_file, 'a') as log:
        log.write('compared FP;'
                  'polynomial degree;'
                  '# minutia points;'
                  '# chaff points;'
                  'thresholds (points/x/y/theta/total/theta basis);'
                  'total coeff size [bits];'
                  '# minutiae candidates;'
                  '# subsets;'
                  '# evaluated subsets;'
                  'encode time [s];'
                  'decode time [s];'
                  'geom table time [s];'
                  'interpolation time [s];'
                  'GH decode time [s];'
                  'total time [s];'
                  '# geom tries;'
                  '# geom single matches;'
                  '# geom table;'
                  '# geom iteration;'
                  'gallery selected basis;'
                  'probe selected basis;'
                  'subsets eval\n')


def print_minutia_basis(m):
    if m is None:
        return "No Basis"
    else:
        return '({}/{}/{})'.format(m.x, m.y, m.theta)


def notify_finish():
    print("Finished all experiments!\n")


if __name__ == '__main__':
    main()
