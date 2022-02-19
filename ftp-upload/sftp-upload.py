#!/usr/bin/env python3

import argparse
import os
import pysftp

srv = pysftp.Connection(host="www.destination.com", username="root",
password="password",log="./temp/pysftp.log")

with srv.cd('public'): #chdir to public
    srv.put('C:\Users\XXX\Dropbox\test.txt') #upload file to nodejs/

# Closes the connection
srv.close()


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
