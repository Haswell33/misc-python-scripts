#!/usr/bin/env python3
# Author: K. Siedlaczek

import ftplib
import argparse
import os


def uploadFilesFtps(src_path, dest_path, ftps_host, ftps_user, ftps_pass):
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    ftps_session = getFtpsConnection(ftps_host, ftps_user, ftps_pass)
    checkIfDestPathExists(ftps_session, dest_path)
    saveFilesFtps(ftps_session, src_path)
    ftps_session.quit()


def getFtpsConnection(host, user, password):
    ftps_session = ftplib.FTP_TLS(host)
    ftps_session.login(user, password)
    ftps_session.prot_p()
    ftps_session.cwd('/')
    return ftps_session


def checkIfDestPathExists(ftps_session, path):
    directories = path.split('/')
    ftps_session.cwd('/')
    for directory in directories:  # checks if ftp_dest_dir exists, if not mkdir
        if directory in ftps_session.nlst():
            ftps_session.cwd(directory)
            print(f'CWD {directory}')
        else:
            ftps_session.mkd(directory)
            print(f'MKD {directory}')
            ftps_session.cwd(directory)
            print(f'CWD {directory}')


def saveFilesFtps(ftps_session, src_path):
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


def parseArgs():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--srcPath', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsHost', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsDir', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsUser', help='', type=str, required=True)
    arg_parser.add_argument('--ftpsPass', help='', type=str, required=True)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parseArgs()
    uploadFilesFtps(args.srcPath, args.ftpsDir, args.ftpsHost, args.ftpsUser, args.ftpsPass)
