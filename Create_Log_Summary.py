"""
    Script to create log summary of all .csv log files in folder db_testing
"""

import os
import csv

from Constants import LOG_SUMMARY_PATH, DB_TESTING_FOLDER, DB_2A_FOLDER, LOG_SUMMARY_2A_PATH, \
    LOG_TOTAL_DB_2A_PATH, LOG_TOTAL_PARAM_2A_PATH, SPLIT_COMPUTATION


def create_log_summary(log_summary_path, db_testing_folder):
    initiate_log_summary(log_summary_path)

    # loop through whole database (folder)
    all_paths = os.listdir(db_testing_folder)

    fvc_flag = False
    one_vs_one_flag = False

    for log_name_original in all_paths:
        if log_name_original.startswith('1_vs_1_'):
            log_name = log_name_original[len('1_vs_1_'):]
            one_vs_one_flag = True
        elif log_name_original.startswith('fvc_'):
            log_name = log_name_original[len('fvc_'):]
            fvc_flag = True
        else:
            log_name = log_name_original

        # only consider db_ logs, param_ logs information are written into same row
        if log_name.startswith('db_'):
            log_info_original = log_name.strip('db_')
            log_info = log_info_original.strip('.csv').split('_')
            assert len(log_info) == 4
            poly = log_info[0].strip('poly')
            minu = log_info[1].strip('minu')
            date = log_info[2]
            time = log_info[3]

            # Determine log file
            if fvc_flag:
                db_log_file = db_testing_folder + 'fvc_' + log_name
            elif one_vs_one_flag:
                db_log_file = db_testing_folder + '1_vs_1_' + log_name
            else:
                db_log_file = db_testing_folder + log_name

            # Read db file and calculate false positives (FMR) and false negatives (FNMR)
            with open(db_log_file) as db_log:
                # headerline
                next(db_log)
                # false positive and false negative totals
                false_positives = 0
                false_negatives = 0
                row_total_db = 0
                genuine_matches = 0
                genuine_non_matches = 0
                for row in csv.reader(db_log, delimiter=';'):
                    row_total_db += 1
                    # if fingers are the same: genuine match
                    if row[0] == row[2]:
                        genuine_matches += 1
                        # match of algorithm is falsch (false) -> should have been true
                        if row[4] == 'falsch' or row[4] == 'invalid probe':
                            false_negatives += 1
                    # fingers are not the same: no genuine match
                    else:
                        genuine_non_matches += 1
                        # match of algorithm is wahr (true) -> should have been false
                        if row[4] == 'wahr':
                            false_positives += 1

            fmr = round(false_positives / genuine_non_matches, 5)
            fnmr = round(false_negatives / genuine_matches, 5)
            print(genuine_matches)
            print(genuine_non_matches)

            if fvc_flag:
                param_log_file = db_testing_folder + 'fvc_' + 'param_' + log_info_original
            elif one_vs_one_flag:
                param_log_file = db_testing_folder + '1_vs_1_' + 'param_' + log_info_original
            else:
                param_log_file = db_testing_folder + 'param_' + log_info_original

            # Read param file and calculate averages
            with open(param_log_file) as param_log:
                # headerline
                next(param_log)
                # metrics
                encode_time_sum = 0
                decode_time_sum = 0
                interpol_time_sum = 0
                total_time_sum = 0
                row_total_param = 0
                first = True
                chaff_points_number = 0
                thresholds = ''
                subset_eval = ''
                for row in csv.reader(param_log, delimiter=';'):
                    encode_time_sum += float(row[9])
                    decode_time_sum += float(row[10])
                    interpol_time_sum += float(row[12])
                    total_time_sum += float(row[14])
                    row_total_param += 1
                    if first:
                        chaff_points_number = int(row[3])
                        thresholds = row[4]
                        if len(row) >= 22:
                            subset_eval = row[21]
                        first = False

            assert row_total_db == row_total_param or int(minu) > 46
            encode_time_avg = round(encode_time_sum / row_total_param, 2)
            decode_time_avg = round(decode_time_sum / row_total_param, 2)
            interpol_time_avg = round(interpol_time_sum / row_total_param, 2)
            total_time_avg = round(total_time_sum / row_total_param, 2)

            log_summary_one_experiment(poly, minu, date, time, chaff_points_number, thresholds, row_total_db,
                                       genuine_non_matches, genuine_matches, false_positives, false_negatives, fmr, fnmr,
                                       encode_time_avg, decode_time_avg, interpol_time_avg, total_time_avg,
                                       subset_eval, log_summary_path)
    print('Finished writing all log summaries')


def log_summary_2a():
    combine_log_files(LOG_TOTAL_DB_2A_PATH, DB_2A_FOLDER, '_db_')
    combine_log_files(LOG_TOTAL_PARAM_2A_PATH, DB_2A_FOLDER, '_param_')

    create_log_summary(LOG_SUMMARY_2A_PATH, DB_2A_FOLDER)


def combine_log_files(log_total_path, folder_path, keyword):
    # clear log
    open(log_total_path, 'w+').close()
    all_paths = os.listdir(folder_path)
    all_paths.sort()
    first_file = True
    with open(log_total_path, 'a') as log_summary:
        for log_name in all_paths:
            if keyword in log_name:
                with open(folder_path + log_name) as log:
                    print('Writing from {}'.format(log_name))
                    header = next(log)
                    if first_file:
                        log_summary.write(header)
                        first_file = False
                    for line in log:
                        log_summary.write(line)
    print('Finished combining {}'.format(log_total_path))


def initiate_log_summary(log_summary_path):
    """ clear log file and add log header for summary logging """
    open(log_summary_path, 'w+').close()
    with open(log_summary_path, 'a') as log:
        log.write('polynomial degree;'
                  '# minutia points;'
                  '# chaff points;'
                  'thresholds (x/y/theta/total/theta basis);'
                  '# matches total;'
                  '# genuine non-matches;'
                  '# genuine matches;'
                  'false positives;'
                  'false negatives;'
                  'FMR;'
                  'FNMR;'
                  'avg encode time [s];'
                  'avg decode time [s];'
                  'avg interpolation time [s];'
                  'avg total time [s];'
                  'subset eval;'
                  'date;'
                  'time\n')


def log_summary_one_experiment(poly, minu, date, time, chaff_points, thresholds, row_total, genuine_non_matches, genuine_matches,
                               false_positives, false_negatives, fmr, fnmr,
                               avg_encode, avg_decode, avg_interpol, avg_total, subset_eval, log_summary_path):
    """ Log one experiment summary to summary log file """
    with open(log_summary_path, 'a') as log_summary:
        log_summary.write('{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n'.format(
            poly, minu, chaff_points, thresholds, row_total, genuine_non_matches, genuine_matches,
            false_positives, false_negatives, fmr, fnmr, avg_encode, avg_decode, avg_interpol,
            avg_total, subset_eval, date, time))
    print('Finished writing summary for poly {} and minu {}'.format(poly, minu))


if __name__ == '__main__':
    if SPLIT_COMPUTATION:
        log_summary_2a()
    else:
        create_log_summary(LOG_SUMMARY_PATH, DB_TESTING_FOLDER)
