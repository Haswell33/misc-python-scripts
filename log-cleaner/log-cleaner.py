#!/usr/bin/env python3

import logging
import logging.config
import argparse
import sys
import os

logging.basicConfig(filename=f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log', format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def clear_logs(src_path):
    # general = CONFIG['GENERAL']
    try:
        files_in_src_path = os.listdir(src_path)  # list all files from dir
    except FileNotFoundError:
        logging.error(f'directory named "{src_path}" was not found')
        print(os.path.basename(__file__) + ': an error has occurred, check logs for more information')
        return
    for src_file in files_in_src_path:
        log_file = src_path + '/' + src_file
        with open(log_file, 'r') as input_file_r:  # open file with read only permissions to readlines() logfile
            num_of_lines = count_num_of_lines(log_file)
            if num_of_lines >= 5000:  # if num of lines in log file is greater than limit, start clearing
                lines = input_file_r.readlines()
                newest_lines = []
                lines_to_save = [x for x in range(int(num_of_lines/2), num_of_lines)]  # collecting half of lines from log file that will be deleted (oldest lines)
                for i, line in enumerate(lines):
                    if i >= num_of_lines/2:
                        if i < len(lines_to_save) - 1:
                            break
                        if i in lines_to_save:
                            newest_lines.append(line)
                file_space = float(os.stat(log_file).st_size)
                with open(log_file, 'w') as input_file_w:  # open file with write only permissions and add newest_lines
                    input_file_w.writelines(newest_lines)
                deleted_space = float(os.stat(log_file).st_size)
                recovered_space = file_space - deleted_space  # count recovered space
                logging.debug(f'{(num_of_lines/2)} lines were removed and {"{:.2f}".format(recovered_space / 1024)}KB of space was recovered from "{src_file}"')
            else:
                logging.info(f'"{src_file}" has not been modified, count {num_of_lines} lines in log file')


def count_num_of_lines(src_path):  # count number of lines in file
    count = 0
    input_file = open(src_path, 'r')
    while 1:
        buffer = input_file.read(8192 * 1024)
        if not buffer:
            break
        count += buffer.count('\n')
    input_file.close()
    return count


def parse_args():
    arg_parser = argparse.ArgumentParser(description='Script checks number of lines in log files, if number is greater then specific number, script cuts a half of lines')
    arg_parser.add_argument('-d', '--logDir', help='Path to dir with logs {-d logDir}', type=str, required=True)
    return arg_parser.parse_args()


def get_params(script_name, list_of_params):
    output_string = script_name + ' '
    for count in range(0, len(list_of_params)):
        output_string += list_of_params[count] + ' '
    return output_string


if __name__ == '__main__':
    args = parse_args()
    validate_and_start(os.path.basename(__file__), args.logDir)
