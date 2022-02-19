#!/usr/bin/env python3

import argparse
import os
import pysftp


class MyConnection(pysftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)


def uploadFileSftp(src_path, dest_path, sftp_host, sftp_user, sftp_pass, sftp_port):
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    cnopts = pysftp.CnOpts()  # do not check key
    cnopts.hostkeys = None
    with MyConnection(sftp_host, username=sftp_user, password=sftp_pass, port=sftp_port, cnopts=cnopts) as sftp_session:
        try:
            sftp_session.cwd(dest_path)
        except FileNotFoundError:
            checkIfDestPathExists(sftp_session, dest_path)
        sftp_session.put(src_path, preserve_mtime=True)


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
    arg_parser = argparse.ArgumentParser(description='Put files from local directory to server directory. Only PasswordAuthentication, does not support PubKeyAuthentication ')
    arg_parser.add_argument('-s', '--srcPath', help='Source directory on local host', type=str, required=True)
    arg_parser.add_argument('-d', '--destPath', help='Destination directory on server', type=str, required=True)
    arg_parser.add_argument('-H', '--sftpHost', help='Host with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-u', '--sftpUser', help='User with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-p', '--sftpPass', help='Password with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-P', '--sftpPort', help='Port number to which the server connects. Default is 22', type=int, default=22)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parseArgs()
    uploadFileSftp(args.srcPath, args.destPath, args.sftpHost, args.sftpUser, args.sftpPass, args.sftPort)
