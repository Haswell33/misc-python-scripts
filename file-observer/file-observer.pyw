import os
import time
import sys
import os
import ftplib
import logging
import argparse
import ctypes.wintypes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CSIDL_PERSONAL = 5  # My Documents
SHGFP_TYPE_CURRENT = 0
buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, SHGFP_TYPE_CURRENT, buf)
logging.basicConfig(filename=buf.value + '/logs/file-observer.log', format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)


class MonitorFile(FileSystemEventHandler):
    def on_created(self, event):
        super(MonitorFile, self).on_created(event)

    def on_modified(self, event):
        super(MonitorFile, self).on_modified(event)
        if filename in event.src_path and not event.src_path.endswith(filename):  # not event.src_path.endswith(filename) because keepass makes update in 1 hour cycle for no reason, but without cache data on the end of filename, this is test condition
            save_to_ftp(ftp_host, ftp_user, ftp_pass, ftp_dir, filename)
            logging.info(f'[LOCAL->FTP] fname={filename}; ftpHost={ftp_host}; event_type={event.event_type}; path={event.src_path}')
        else:
            logging.info(f'{filename} has triggered on_modified event, but was not modified')  # for test

    def on_deleted(self, event):
        super(MonitorFile, self).on_deleted(event)


def save_to_ftp(ftp_host, ftp_user, ftp_pass, ftp_dir, filename):
    directories = ftp_dir.split('/')
    ftp_session = _get_ftp_connection(ftp_host, ftp_user, ftp_pass)
    ftp_session.cwd('/')
    for directory in directories:
        if directory in ftp_session.nlst():
            ftp_session.cwd(directory)
        else:
            ftp_session.mkd(directory)
            ftp_session.cwd(directory)
    with open(filename, 'rb') as output_file:
        ftp_session.storbinary(f'STOR /{ftp_dir}/{filename}', output_file)
    ftp_session.quit()


def _get_ftp_connection(host, username, password):
    ftp_session = ftplib.FTP(host)
    ftp_session.login(username, password)
    return ftp_session


def parse_args():
    parser = argparse.ArgumentParser(description='Checks if file has been modified')
    parser.add_argument('--fname', help='filename', type=str, required=True)
    parser.add_argument('--ftpHost', help='address of ftp host', type=str, required=True)
    parser.add_argument('--ftpUser', help='username of ftp host', type=str, required=True)
    parser.add_argument('--ftpPass', help='password of ftp host', type=str, required=True)
    parser.add_argument('--ftpDir', help='dest dir to check of ftp host', type=str, required=True)
    return parser.parse_args()

args = parse_args()
ftp_host = args.ftpHost
ftp_user = args.ftpUser
ftp_pass = args.ftpPass
ftp_dir = args.ftpDir
filename = args.fname

if __name__ == "__main__":
    time.sleep(10)
    logging.info(f'[{os.path.basename(__file__)} started]')
    event_handler = MonitorFile()
    observer = Observer()
    observer.schedule(event_handler, path=os.getcwd(), recursive=True)
    observer.start()
    logging.info('[Observer started]')
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.warning('[Observer stopped]')
        observer.stop()
    observer.join()
