#!/usr/bin/env python3

import os
import pysftp
import logging
import argparse
import sys
import errno
import ctypes.wintypes

CSIDL_PERSONAL = 5  # My Documents
SHGFP_TYPE_CURRENT = 0
MY_DOCUMENTS = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, MY_DOCUMENTS)
logging.basicConfig(filename=f'{MY_DOCUMENTS.value}/logs/file-observer.log', format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.DEBUG)


class MyConnection(pysftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)


def checkFilesMtime(src_path, dest_path, sftp_host, sftp_user, sftp_pass, sftp_port):  # compare mtime of local file and sftp file, if sftp is newer download to local dir
    file = src_path.rsplit('/', 1)[-1]  # extract filename from full path
    cnopts = pysftp.CnOpts()  # do not check key
    cnopts.hostkeys = None
    local_file_mtime = os.path.getmtime(src_path)  # mtime of local file
    with MyConnection(sftp_host, username=sftp_user, password=sftp_pass, port=sftp_port, cnopts=cnopts, log=False) as sftp_session:
        sftp_session.cwd(dest_path)
        sftp_file_mtime = sftp_session.stat(file).st_mtime  # mtime of server file
        if sftp_file_mtime > local_file_mtime and sftp_file_mtime - local_file_mtime > 3:  # if mtime of sftp file is newer and difference between two files is at least two seconds do if()
            downloadFile(sftp_session, src_path, dest_path, file)
            logging.debug(f'[SFTP->LOCAL] path={src_path}; serverHost={sftp_host}')
        else:
            logging.info(f'mtime of local file is newer, file not downloaded')


def downloadFile(sftp_session, src_path, dest_path, file):  # download file from SFTP
    try:
        sftp_session.cwd(dest_path)
    except FileNotFoundError:
        checkIfDestPathExists(sftp_session, dest_path)
    sftp_session.get(sftp_session.pwd + '/' + file, src_path, preserve_mtime=True)


def checkIfDestPathExists(sftp_session, path):
    directories = path.split('/')
    sftp_session.cwd('/')
    for directory in directories:
        if directory in sftp_session.listdir():
            sftp_session.cwd(directory)
            print(f'CWD {sftp_session.getcwd()}')
        else:
            sftp_session.mkdir(directory)
            print(f'MKDIR {directory}')
            sftp_session.cwd(directory)
            print(f'CWD {sftp_session.getcwd()}')


def parseArgs():
    arg_parser = argparse.ArgumentParser(description='Compares modification time of local file and a file with the same name on the SFTP server. '
                                                     'If the modification time of file on SFTP server is newer, the script will replace the local file with the file from the server')
    arg_parser.add_argument('-s', '--srcPath', help='Source file on local host', type=str, required=True)
    arg_parser.add_argument('-d', '--destPath', help='Destination directory on server where file is stored', type=str, required=True)
    arg_parser.add_argument('-H', '--sftpHost', help='Host with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-u', '--sftpUser', help='User with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-p', '--sftpPass', help='Password with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-P', '--sftpPort', help='Port number to which the server connects. Default is 22', type=int, default=22)
    return arg_parser.parse_args()


if __name__ == "__main__":
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.info(f'[{os.path.basename(__file__)} started]')
    args = parseArgs()
    if not os.path.isfile(args.srcPath):
        logging.error(f'{os.path.basename(__file__)}: {FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.srcPath)}')
        logging.info(f'[{os.path.basename(__file__)} stopped]')
        sys.exit(0)
    checkFilesMtime(args.srcPath, args.destPath, args.sftpHost, args.sftpUser, args.sftpPass, args.sftpPort)
