#!/usr/bin/env python3

import argparse
import os
import pysftp


def uploadFilesSftp(src_path, dest_path, sftp_host, sftp_user, sftp_pass):
    if not os.path.exists(src_path):
        return
    with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_pass, port=2222) as sftp:
        sftp.cwd(dest_path)
        sftp.put(src_path)
    #ftps_session = getSftpConnections(dest_ftps_host, dest_ftps_user, dest_ftps_pass)
    #checkIfDestPathExists(ftps_session, dest_path)
    #saveFilesFtps(ftps_session, src_path)
    #ftps_session.quit()


def parseArgs():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--srcPath', help='', type=str, required=True)
    arg_parser.add_argument('--sftpHost', help='', type=str, required=True)
    arg_parser.add_argument('--sftpDir', help='', type=str, required=True)
    arg_parser.add_argument('--sftpUser', help='', type=str, required=True)
    arg_parser.add_argument('--sftpPass', help='', type=str, required=True)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parseArgs()
    uploadFilesSftp(args.srcPath, args.sftpDir, args.sftpHost, args.sftpUser, args.sftpPass)
