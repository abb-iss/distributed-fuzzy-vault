""" Application for distributed fingerprint recognition using fuzzy vault """


from subprocess import Popen, PIPE
import time
import os

from Strings import *
from Constants import *
from Main import initialize_log_dict, generate_smallest_secret, generate_vault, verify_secret, store_in_cosmos_db, \
    retrieve_from_cosmos_db
from DBHandler import DBHandler
from Adafruit_Handler import AdafruitHandler


def run_app(renew_log=False):
    print('========================================================================')
    print(APP_WELCOME)
    print('========================================================================')
    print('\n')

    # calculating secret length according to poly degree and crc
    secret_length = len(generate_smallest_secret(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=False)) * 8
    # initialize log
    if not os.path.exists('out'):
        os.makedirs('out')
    if renew_log:
        initialize_app_log(LOG_FILE_APP)
    running = True
    while running:
        # list options for user
        print(APP_CHOOSE_FUNCTION)
        for key in APP_FUNCTIONAILTIES.keys():
            print("%s: %s" % (key, APP_FUNCTIONAILTIES[key]))
        print()

        # get input option from user
        correct_option = False
        input_option = ''
        while not correct_option:
            input_option = input(APP_DESIRED_OPTION)
            if input_option not in APP_FUNCTIONAILTIES.keys():
                print(APP_OPTION_FALSE)
            else:
                correct_option = True

        # create DB handler
        db_handler = DBHandler()
        # initiate log
        app_log_dict = dict()
        initialize_app_log_dict(app_log_dict)
        # Exit application
        if input_option == list(APP_FUNCTIONAILTIES.keys())[2]:
            running = False
            print(APP_BYE)
        # Enroll new fingerprint
        elif input_option == list(APP_FUNCTIONAILTIES.keys())[0]:
            app_log_dict['action'] = 'ENCODE'
            new_id = get_id()
            app_log_dict['vault_id'] = new_id
            print(APP_SCAN_FP)
            # Scanning fingerprint, recapture if not enough good minutiae
            good_fp = False
            capture_time_start = time.time()
            capture_time_end = time.time()
            while not good_fp:
                capture_time_start = time.time()
                good_fp = capture_new_fp_xyt(new_id)
                capture_time_end = time.time()
                if not good_fp:
                    print(APP_RETRY_FP)
            app_log_dict['capture_time'] = round(capture_time_end - capture_time_start, 2)
            action_fp_time = time.time()
            enroll_new_fingerprint(db_handler, new_id, FP_TEMP_FOLDER + FP_OUTPUT_NAME + new_id + '.xyt', app_log_dict)
            print('\n')
            print('Execution time fuzzy vault algorithm including DB: {}'.format(round(time.time() - action_fp_time, 2)))
            write_app_log(LOG_FILE_APP, app_log_dict)
            remove_temp_files(new_id)
        # Verify fingerprint
        elif input_option == list(APP_FUNCTIONAILTIES.keys())[1]:
            app_log_dict['action'] = 'DECODE'
            id_to_verify = get_id()
            app_log_dict['vault_id'] = id_to_verify
            print(APP_SCAN_FP)
            # Scanning fingerprint, recapture if not enough good minutiae
            good_fp = False
            while not good_fp:
                capture_time_start = time.time()
                good_fp = capture_new_fp_xyt(id_to_verify)
                capture_time_end = time.time()
                if not good_fp:
                    print(APP_RETRY_FP)
            app_log_dict['capture_time'] = round(capture_time_end - capture_time_start, 2)
            action_fp_time = time.time()
            verify_fingerprint(db_handler, id_to_verify, FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_to_verify + '.xyt',
                               secret_length, app_log_dict)
            print('\n')
            print('Execution time fuzzy vault algorithm including DB: {}'.format(round(time.time() - action_fp_time, 2)))
            write_app_log(LOG_FILE_APP, app_log_dict)
            remove_temp_files(id_to_verify)
        else:
            print(APP_ERROR)
        print('========================================================================')
        print('\n')
        time.sleep(1)
        db_handler.close_handler()


def get_id():
    correct_id = False
    new_id = 0
    while not correct_id:
        new_id = input(APP_NEW_ID)
        if new_id.isdigit():
            new_id = int(new_id)
            correct_id = True
        else:
            print(APP_ID_ERROR)
    return str(new_id)


def capture_new_fp_xyt(id_number):
    """
    Capture new fingerprint image with Adafruit sensor.
    Convert .bmp to .jpg
    Use mindtct to extract .xyt file from .jpg
    Check if there are enough minutiae detected according to MINUTIAE_POINTS_AMOUNT
    :return: True if enough minutiae detected, else False
    """
    try:
        AdafruitHandler.download_fingerprint(id_number)
    except Exception:
        return False

    run_mindtct(FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + '.jpg', id_number)

    # amount of minutiae in .xyt
    num_lines = sum(1 for _ in open(FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + '.xyt'))
    if num_lines >= MINUTIAE_POINTS_AMOUNT:
        return True
    else:
        print('Unfortunately, only {} minutiae were found...'.format(num_lines))
        return False


def enroll_new_fingerprint(db_handler, vault_id, xyt_path, app_log_dict):
    # calculate secret according to polynomial degree. secret has to be able to be encoded in bytes (*8)
    encode_time_start = time.time()
    secret_bytes = generate_smallest_secret(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=False)
    print(APP_FV_SECRET)

    log_dict = dict()
    initialize_log_dict(log_dict)

    fuzzy_vault = generate_vault(xyt_path, MINUTIAE_POINTS_AMOUNT, CHAFF_POINTS_AMOUNT, POLY_DEGREE,
                                 secret_bytes, CRC_LENGTH, GF_2_M, log_dict, echo=False)
    print(APP_FV_GENERATED)
    encode_time_end = time.time()
    app_log_dict['action_time'] = round(encode_time_end - encode_time_start, 2)

    # send vault to database
    try:
        db_time_start = time.time()
        store_in_cosmos_db(db_handler, fuzzy_vault, vault_id)
        db_time_end = time.time()
        app_log_dict['db_time'] = round(db_time_end - db_time_start, 2)
    except Exception as e:
        print('Exception message: ' + str(e))
        print('Error occurred during database handling.')
        app_log_dict['success'] = 'FAILURE'
        return
    print(APP_FV_SENT_DB)
    print('\n')
    print(APP_ENROLL_SUCCESS)
    app_log_dict['success'] = 'SUCCESS'
    return


def verify_fingerprint(db_handler, vault_id, xyt_path, secret_length, app_log_dict):
    log_dict = dict()
    initialize_log_dict(log_dict)
    db_time_start = time.time()
    db_vault = retrieve_from_cosmos_db(db_handler, vault_id)
    db_time_end = time.time()
    app_log_dict['db_time'] = round(db_time_end - db_time_start, 2)
    if db_vault:
        decode_time_start = time.time()
        db_vault.create_geom_table()
        success = verify_secret(xyt_path, MINUTIAE_POINTS_AMOUNT, POLY_DEGREE, CRC_LENGTH, secret_length,
                                GF_2_M, db_vault, log_dict, echo=False)
        db_vault.clear_vault()
        decode_time_end = time.time()
        app_log_dict['action_time'] = round(decode_time_end - decode_time_start, 2)
        if success:
            print(APP_VERIFY_SUCCESS)
            app_log_dict['success'] = 'SUCCESS'
            return
        else:
            print(APP_VERIFY_FAILURE)
            app_log_dict['success'] = 'FAILURE'
            return
    else:
        print(APP_VERIFY_FAILURE)
        app_log_dict['success'] = 'FAILURE'
        return


def run_mindtct(jpg_path, id_number):
    """ Runs mindtct on xyt file path"""
    mindtct = Popen(['mindtct', jpg_path, FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number], stdout=PIPE, stderr=PIPE)
    mindtct.communicate()


def remove_temp_files(id_number):
    """ Remove all temp files generated by mindtct """
    process = Popen(['rm', FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + '*'], stdout=PIPE, stderr=PIPE)
    process.communicate()


def initialize_app_log_dict(app_log_dict):
    app_log_dict['action'] = 'encode or decode'
    app_log_dict['capture_time'] = 0
    app_log_dict['db_time'] = 0
    app_log_dict['action_time'] = 0
    app_log_dict['success'] = 'FAILURE'
    app_log_dict['vault_id'] = 0


def initialize_app_log(log_path):
    """ clear log file and add log header for logging app testing """
    open(log_path, 'w+').close()
    with open(log_path, 'a') as log:
        log.write('action;'
                  'action time [s];'
                  'capture time [s];'
                  'db time [s];'
                  'success;'
                  'date;'
                  'time;'
                  'vault id\n')


def write_app_log(log_path, app_log_dict):
    """ write one line in log app testing """
    datetime_now = datetime.datetime.now()
    date_now = datetime_now.strftime("%Y%m%d")
    time_now = datetime_now.strftime("%H%M")
    action = app_log_dict['action']
    action_time = app_log_dict['action_time']
    capture_time = app_log_dict['capture_time']
    db_time = app_log_dict['db_time']
    success = app_log_dict['success']
    vault_id = app_log_dict['vault_id']
    with open(log_path, 'a') as log:
        log.write('{};{};{};{};{};{};{};{}\n'.format(action, action_time, capture_time, db_time, success,
                                                     date_now, time_now, vault_id))


if __name__ == '__main__':
    run_app(renew_log=False)
