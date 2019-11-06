""" All changeable constants for fuzzy vault """

import datetime

# Constants database run

# How many times the database is iterated through (at each iteration, parameters can be changed below
# with CHANGE_* constants.
RUN_DB_ITERATIONS = 4
# Reuse generated vault for the same gallery template
REUSE_VAULT = True
# Threshold to define when to use random subset evaluation
SUBSET_EVAL_THRES = 25
# Use random subset evaluation instead of generation of all subsets upfront
RANDOM_SUBSET_EVAL = True
# Run 1vs1 and FVC protocol instead of all possible matches
ONE_TO_ONE_FVC_PROTOCOL = True
# Check if chaff point mapping is on polynomial
CHECK_CHAFF_POINT_MAPPING = True

# Constants variable
POLY_DEGREE = 8
MINUTIAE_POINTS_AMOUNT = 30
CHAFF_POINTS_AMOUNT = 300

# Parameter testing changes after each DB run, used in change_parameters()
CHANGE_POLY = 0
CHANGE_MINU_POINTS = 0
CHANGE_CHAFF_POINTS = 0
CHANGE_POINTS_DIST = 0
CHANGE_X_THRES = 0
CHANGE_Y_THRES = 0
CHANGE_THETA_THRES = 0
CHANGE_TOT_THRES = 0
CHANGE_BASIS_THETA = 0

# Distance that minutiae (genuine minutiae and chaff points) have to at least be apart
POINTS_DISTANCE = 10

# Constants Vault_Verifier
X_THRESHOLD = 12
Y_THRESHOLD = 12
THETA_THRESHOLD = 12
TOTAL_THRESHOLD = 25
BASIS_THETA_THRESHOLD = 10
# max threshold expected in fingerprint picture
MAX_ITERATION_THRESHOLD = 27000000
# threshold for geometric hashing: should be exactly POLY_DEGREE + 1 to ensure correctness
MATCH_THRESHOLD = POLY_DEGREE + 1
# Logging in Vault_Verifier
now = datetime.datetime.now()
date_time_now_str = '{}_{}'.format(now.strftime("%Y%m%d"), now.strftime("%H%M"))
LOG_PATH = 'out/vault_minutiae_{}.log'.format(date_time_now_str)
LOG_CANDIDATES_PATH_PREFIX = 'out/candidate_minutiae_{}_'.format(date_time_now_str)
LOG_CANDIDATES_PATH_SUFFIX = '.csv'

# input files
XYT_GALLERY = '10_5.xyt'
XYT_PROBE = '10_2.xyt'
DATABASE_2B_PATH = 'input_images/FVC2006_DB_2B/'
FP_TEMP_FOLDER = 'fp_temp/'
FP_BMP_IMAGE = '1_1R_19.bmp'
FP_OUTPUT_NAME = 'temp'

# Constants fixed
# Galois field exponent
GF_2_M = 32
CRC_LENGTH = 32

# Constants to run over whole DB 2A
SPLIT_COMPUTATION = False
# Computation including FINGER_START (CAPTURE_START), excluding FINGER_END (CAPTURE_END)
FINGER_START = 1
FINGER_END = 21
CAPTURE_START = 1
CAPTURE_END = 13
DATABASE_2A_PATH = 'input_images/FVC2006_DB_2A/'
DATABASE_2A_FLAG = True

# Logging
LOG_VAULT_MINUTIAE = True
LOG_CANDIDATE_MINUTIAE = False
LOG_PARAM = 'param_poly{}_minu{}_{}.csv'.format(
    POLY_DEGREE, MINUTIAE_POINTS_AMOUNT, date_time_now_str)
LOG_DB = 'db_poly{}_minu{}_{}.csv'.format(
    POLY_DEGREE, MINUTIAE_POINTS_AMOUNT, date_time_now_str)
LOG_FILE_PARAMETER_TESTING = 'out/' + LOG_PARAM
LOG_FILE_DATABASE_TESTING = 'out/' + LOG_DB
# Logging database 2A (partial)
LOG_FILE_PARAMETER_2A = 'out/{}_{}_param_2A.csv'.format(FINGER_START, FINGER_END - 1)
LOG_FILE_DATABASE_2A = 'out/{}_{}_db_2A.csv'.format(FINGER_START, FINGER_END - 1)
# Logging app
LOG_FILE_APP = 'out/app_{}.csv'.format(now.strftime("%Y%m%d"))

# Flags for running through database
SAVE_VAULT_TO_DB = False
GET_VAULT_FROM_DB = False

# JSON key words (from key / value pairs)
JSON_VAULT_ID = "vault_id"
JSON_VAULT_X = "vault_x"
JSON_VAULT_Y = "vault_y"
JSON_VAULT_GEOM = "vault_geom_table"
JSON_GEOM_BASIS = "geom_basis"
JSON_GEOM_X = "geom_x"
JSON_GEOM_Y = "geom_y"

# Constants for Create_Log_Summary script
DB_TESTING_FOLDER = 'db_testing/1vs1/'
LOG_SUMMARY_PATH = DB_TESTING_FOLDER + 'test_summary_all_{}.csv'.format(date_time_now_str)
DB_2A_FOLDER = DB_TESTING_FOLDER + 'DB_2A/'
LOG_SUMMARY_2A_PATH = DB_2A_FOLDER + 'test_summary_all_{}.csv'.format(date_time_now_str)
LOG_TOTAL_DB_2A_PATH = DB_2A_FOLDER + 'db_poly{}_minu{}_{}.csv'.format(
    POLY_DEGREE, MINUTIAE_POINTS_AMOUNT, date_time_now_str)
LOG_TOTAL_PARAM_2A_PATH = DB_2A_FOLDER + 'param_poly{}_minu{}_{}.csv'.format(
    POLY_DEGREE, MINUTIAE_POINTS_AMOUNT, date_time_now_str)
