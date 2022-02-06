#!/usr/bin/env python3

import argparse
import os


def upload_local_files_to_ftp(src_path, dest_path, dest_sftp_host, dest_sftp_user, dest_sftp_pass):
    if not os.path.exists(src_path):
        return
    # sftp_session = get_SFTP_connection(dest_sftp_host, dest_sftp_user, dest_sftp_pass)
    # check_if_dest_path_exists(sftp_session, dest_path)
    # send_recursive_files_on_sftp(sftp_session, src_path)
    # ftp_session.quit()


def get_SFTP_connection(sftp_host, sftp_user, sftp_pass):
    pass


def check_if_dest_path_exists(sftp_session, path):
    pass


def send_recursive_files_on_sftp(sftp_session, src_path):
    pass


def parse_args():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--srcPath', help='', type=str, required=True)
    arg_parser.add_argument('--sftpHost', help='', type=str, required=True)
    arg_parser.add_argument('--sftpDir', help='', type=str, required=True)
    arg_parser.add_argument('--sftpUser', help='', type=str, required=True)
    arg_parser.add_argument('--sftpPass', help='', type=str, required=True)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    upload_local_files_to_sftp(args.srcPath, args.sftpDir, args.sftpHost, args.sftpUser, args.sftpPass)
