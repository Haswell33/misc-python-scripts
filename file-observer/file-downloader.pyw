#!/usr/bin/env python3

import os
import ftplib
import logging
import argparse
import sys
import errno
import ctypes.wintypes
from datetime import datetime
from dateutil import parser

CSIDL_PERSONAL = 5  # My Documents
SHGFP_TYPE_CURRENT = 0
MY_DOCUMENTS = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, MY_DOCUMENTS)
logging.basicConfig(filename=MY_DOCUMENTS.value + '/logs/file-observer.log', format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)


def check_timestamp_of_file(path_to_file, ftp_host, ftp_user, ftp_pass, ftp_dir):  # check modified time of files, if file in ftp is newer fun will retr it to local storage
    local_timestamp = datetime.strptime(datetime.fromtimestamp(os.path.getmtime(f'{path_to_file}')).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    filename = path_to_file.rsplit('/', 1)[-1]
    ftp_session = _get_ftp_connection(ftp_host, ftp_user, ftp_pass)
    ftp_session.cwd(ftp_dir)
    ftp_timestamp = ftp_session.voidcmd('MDTM ' + filename)[4:].strip()
    ftp_timestamp = parser.parse(ftp_timestamp)
    difference_between_timestamps = divmod((ftp_timestamp - local_timestamp).total_seconds(), 60)
    if local_timestamp < ftp_timestamp and difference_between_timestamps[0] > 2.0:
        download_file(ftp_session, path_to_file, filename)
        ftp_session.quit()
        return True
    else:
        ftp_session.quit()
        return False


def download_file(ftp_session, path_to_file, filename):
    with open(path_to_file, 'wb') as file:
        ftp_session.retrbinary(f'RETR {filename}', file.write)


def _get_ftp_connection(host, user, password):
    ftp_session = ftplib.FTP(host)
    ftp_session.login(user, password)
    return ftp_session


def parse_args():
    parser = argparse.ArgumentParser(description='Checks if modified time of file on dest ftp server is newer than local file with that same name')
    parser.add_argument('--pathToFile', help='path to file', type=str, required=True)
    parser.add_argument('--ftpHost', help='address of ftp host', type=str, required=True)
    parser.add_argument('--ftpUser', help='username of ftp host', type=str, required=True)
    parser.add_argument('--ftpPass', help='password of ftp host', type=str, required=True)
    parser.add_argument('--ftpDir', help='dest dir to check of ftp host', type=str, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    logging.info(f'[{os.path.basename(__file__)} started]')
    args = parse_args()
    if not os.path.isfile(args.pathToFile):
        logging.error(f'{os.path.basename(__file__)}: {FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.pathToFile)}')
        logging.info(f'[{os.path.basename(__file__)} stopped]')
        sys.exit(0)
    if check_timestamp_of_file(args.pathToFile, args.ftpHost, args.ftpUser, args.ftpPass, args.ftpDir):
        logging.info(f'[FTP->LOCAL] path={args.pathToFile}; ftpHost={args.ftpHost}')