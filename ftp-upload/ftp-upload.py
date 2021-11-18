#!/usr/bin/env python3

import ftplib
import argparse
import os


def upload_local_files_to_ftp(src_path, dest_path, dest_ftp_host, dest_ftp_user, dest_ftp_pass):
    if not os.path.exists(src_path):
        return
    ftp_session = get_FTP_connection(dest_ftp_host, dest_ftp_user, dest_ftp_pass)
    check_if_dest_path_exists(ftp_session, dest_path)
    send_recursive_files_on_ftp(ftp_session, src_path)
    ftp_session.quit()


def get_FTP_connection(ftp_host, ftp_user, ftp_pass):
    ftp_session = ftplib.FTP(ftp_host)
    ftp_session.login(ftp_user, ftp_pass)
    ftp_session.cwd('/')
    return ftp_session


def check_if_dest_path_exists(ftp_session, path):
    directories = path.split('/')
    ftp_session.cwd('/')
    for directory in directories:  # checks if ftp_dest_dir exists, if not mkdir
        if directory in ftp_session.nlst():
            ftp_session.cwd(directory)
        else:
            ftp_session.mkd(directory)
            ftp_session.cwd(directory)


def send_recursive_files_on_ftp(ftp_session, src_path):
    def stor_on_ftp(ftp_session, src_path):
        for src_file in os.listdir(src_path):
            src_local_path = os.path.join(src_path, src_file)
            if os.path.isfile(src_local_path):
                with open(f'{src_path}/{src_file}', 'rb') as input_file:
                    print(f'STOR {ftp_session.pwd()}/{src_file}')
                    ftp_session.storbinary(f'STOR {ftp_session.pwd()}/{src_file}', input_file)
            elif os.path.isdir(src_local_path):
                print(f'MKD {src_local_path}')
                try:
                    ftp_session.mkd(src_file)
                except ftplib.error_perm as error_msg:
                    if not error_msg.args[0].startswith('550'):
                        raise
                print(f'CWD {src_file}')
                ftp_session.cwd(src_file)
                print(f'PWD {ftp_session.pwd()}')
                stor_on_ftp(ftp_session, src_local_path)
                print('CWD ..')
                ftp_session.cwd('..')
    stor_on_ftp(ftp_session, src_path)


def parse_args():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--srcPath', help='', type=str, required=True)
    arg_parser.add_argument('--ftpHost', help='', type=str, required=True)
    arg_parser.add_argument('--ftpDir', help='', type=str, required=True)
    arg_parser.add_argument('--ftpUser', help='', type=str, required=True)
    arg_parser.add_argument('--ftpPass', help='', type=str, required=True)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    upload_local_files_to_ftp(args.srcPath, args.ftpDir, args.ftpHost, args.ftpUser, args.ftpPass)
