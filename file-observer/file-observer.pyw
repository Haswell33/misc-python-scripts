#!/usr/bin/env python3

import os
import sys
import time
import os
import pysftp
import errno
import logging
import argparse
import ctypes.wintypes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CSIDL_PERSONAL = 5  # My Documents
SHGFP_TYPE_CURRENT = 0
MY_DOCUMENTS = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, MY_DOCUMENTS)
logging.basicConfig(filename=f'{MY_DOCUMENTS.value}/logs/{os.path.basename(__file__).split(".")[0]}.log', format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.DEBUG)


class MyConnection(pysftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)


class MonitorFile(FileSystemEventHandler):
    __slots__ = ['src_path', 'dest_path', 'sftp_host', 'sftp_user', 'sftp_pass', 'sftp_port', 'file']

    def __init__(self, args):
        self.src_path = args.srcPath
        self.dest_path = args.destPath
        self.sftp_host = args.sftpHost
        self.sftp_user = args.sftpUser
        self.sftp_pass = args.sftpPass
        self.sftp_port = args.sftpPort
        self.file = args.srcPath.rsplit('/', 1)[-1]  # extract filename from full path

    def on_modified(self, event):
        super(MonitorFile, self).on_modified(event)
        if self.file in event.src_path and '.kdbx' in self.file:  # not event.src_path.endswith(filename) because keepass makes update in 1 hour cycle for no reason, but without cache value on the end of filename, this is test condition
            if not event.src_path.endswith(self.file):
                uploadFile(self.src_path, self.dest_path, self.sftp_host, self.sftp_user, self.sftp_pass, self.sftp_port)
                logging.debug(f'[LOCAL->SFTP] path="{self.src_path}"; serverHost={self.src_path}; eventType={event.event_type}; cacheValue={event.src_path.rsplit(".", 1)[-1]}')
            else:
                logging.debug(f'{self.src_path} has triggered on_modified event, but was not modified')  # for test
        elif self.file in event.src_path:  # common situation
            uploadFile(self.src_path, self.dest_path, self.sftp_host, self.sftp_user, self.sftp_pass, self.sftp_port)
            logging.debug(f'[LOCAL->SFTP] path="{self.src_path}"; serverHost={self.sftp_host}; event_type={event.event_type}')


def uploadFile(src_path, dest_path, sftp_host, sftp_user, sftp_pass, sftp_port):
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    cnopts = pysftp.CnOpts()  # do not check key
    cnopts.hostkeys = None
    with MyConnection(sftp_host, username=sftp_user, password=sftp_pass, port=sftp_port, cnopts=cnopts, log=0) as sftp_session:
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
    arg_parser = argparse.ArgumentParser(description='Monitor file in directory.')
    arg_parser.add_argument('-s', '--srcPath', help='Source file on local host', type=str, required=True)
    arg_parser.add_argument('-d', '--destPath', help='Destination directory on server where file is stored', type=str, required=True)
    arg_parser.add_argument('-H', '--sftpHost', help='Host with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-u', '--sftpUser', help='User with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-p', '--sftpPass', help='Password with which the server will connect', type=str, required=True)
    arg_parser.add_argument('-P', '--sftpPort', help='Port number to which the server connects. Default is 22', type=int, default=22)
    return arg_parser.parse_args()


if __name__ == "__main__":
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    event_handler = MonitorFile(parseArgs())
    logging.info(f'[{os.path.basename(__file__)} started]')
    if not os.path.isfile(event_handler.src_path):
        logging.error(f'{os.path.basename(__file__)}: {FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), event_handler.src_path)}')
        logging.info(f'[{os.path.basename(__file__)} stopped]')
        sys.exit(0)
    observer = Observer()
    observer.schedule(event_handler, path=event_handler.src_path.rsplit('/', 1)[0], recursive=True)  # only dirpath without file
    time.sleep(10)
    logging.info('[Observer started]')
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info('[Observer stopped]')
        observer.stop()
    observer.join()
