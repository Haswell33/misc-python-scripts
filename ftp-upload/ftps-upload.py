#!/usr/bin/env python3
# Author: K. Siedlaczek

import ftplib
import argparse
import os


def upload_local_files_to_ftps(src_path, dest_path, dest_ftps_host, dest_ftps_user, dest_ftps_pass):
    if not os.path.exists(src_path):
        return
    ftps_session = get_ftps_connection(dest_ftps_host, dest_ftps_user, dest_ftps_pass)
    check_if_dest_path_exists(ftps_session, dest_path)
    send_recursive_files_on_ftps(ftps_session, src_path)
    ftps_session.quit()


def get_ftps_connection(host, user, password):
    ftps_session = ftplib.FTP_TLS(host)
    ftps_session.login(user, password)
    ftps_session.prot_p()
    ftps_session.cwd('/')
    return ftps_session


def check_if_dest_path_exists(ftps_session, path):
    directories = path.split('/')
    ftps_session.cwd('/')
    for directory in directories:  # checks if ftp_dest_dir exists, if not mkdir
        if directory in ftps_session.nlst():
            ftps_session.cwd(directory)
        else:
            ftps_session.mkd(directory)
            ftps_session.cwd(directory)


def send_recursive_files_on_ftps(ftps_session, src_path):
    def stor_on_ftps(ftps_session, src_path):
        for src_file in os.listdir(src_path):
            src_local_path = os.path.join(src_path, src_file)
            if os.path.isfile(src_local_path):
                with open(f'{src_path}/{src_file}', 'rb') as input_file:
                    print(f'STOR {ftps_session.pwd()}/{src_file}')
                    ftps_session.storbinary(f'STOR {ftps_session.pwd()}/{src_file}', input_file)
            elif os.path.isdir(src_local_path):
                print(f'MKD {src_local_path}')
                try:
                    ftps_session.mkd(src_file)
                except ftplib.error_perm as error_msg:
                    if not error_msg.args[0].startswith('550'):
                        raise
                print(f'CWD {src_file}')
                ftps_session.cwd(src_file)
                print(f'PWD {ftps_session.pwd()}')
                stor_on_ftps(ftps_session, src_local_path)
                print('CWD ..')
                ftps_session.cwd('..')
    stor_on_ftps(ftps_session, src_path)


def parse_args():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--srcPath', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsHost', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsDir', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsUser', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsPass', help='', type=str, required=True)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    upload_local_files_to_ftps(args.srcPath, args.ftpsDir, args.ftpsHost, args.ftpsUser, args.ftpsPass)
