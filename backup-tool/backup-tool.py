#!/usr/bin/env python3

# Script to make backups using rsync protocol

import os
import logging
import shutil
import re
import sys
import time
import argparse
from dateutil.relativedelta import relativedelta
from datetime import datetime

logging.basicConfig(filename=f'{os.path.abspath(os.path.dirname(__file__))}/logs/backup-tool.log', format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

RSYNC_DESKTOP_PASS = 'testpass'


def make_backup(src_dir, dest_dir, src_host, max_num_of_backups):
    backup_filename = f'backup-{_get_today()}'
    if not src_host == 'localhost':
        remote_backup(src_dir, dest_dir, src_host, backup_filename)
    else:
        local_backup(src_dir, dest_dir, backup_filename)
    if _get_num_of_backups(dest_dir) > max_num_of_backups:
        remove_oldest_backup(dest_dir)
    logging.info(f'Creating backup "{dest_dir}/{backup_filename}" completed successfully')


def local_backup(src_dirs, dest_dir, backup_filename):
    src_local_dir = ''
    for src_dir in src_dirs:
        src_local_dir = f'{src_local_dir} "{src_dir}"'
    src_local_dir = src_local_dir[1:]
    print(f'rsync -a {src_local_dir} "{dest_dir}/{backup_filename}"')


def remote_backup(src_dirs, dest_dir, src_host, backup_filename):
    src_remote_dir = ''
    start_desktop(src_host)
    for src_dir in src_dirs:
        src_remote_dir = f'{src_remote_dir} "rsync://{src_host}/{src_dir}"'
    src_remote_dir = src_remote_dir[1:]
    print(f'RSYNC_PASSWORD={RSYNC_DESKTOP_PASS} rsync -a {src_remote_dir} "{dest_dir}/{backup_filename}"')
    # os.system()


def remove_oldest_backup(dest_dir):
    oldest_backup = min(os.listdir(dest_dir), key=lambda dirs: os.path.getctime(os.path.join(dest_dir, dirs)))  # looking for the file with the oldest modified date
    try:
        shutil.rmtree(f'{dest_dir}/{oldest_backup}')
        logging.debug(f'Deleting backup "{dest_dir}/{oldest_backup}" completed successfully')
    except PermissionError as error_msg:
        logging.error(f'PermissionError: {str(error_msg)}')
        print(f'{os.path.basename(__file__)}: an error has occurred, check logs for more information')
        return


def start_desktop(host):
    start_timestamp = _get_datetime_object(datetime.now().strftime('%H:%M:%S'))
    end_timestamp = start_timestamp + relativedelta(minutes=+2)  # setting up timeout for 120 seconds
    ip_address = re.findall(r'(?<=@)[^\]]+', host)[0]
    waiting = True
    # os.system(f'./remote-task.py -o start -n desktop')
    while waiting:
        ping_response = os.system(f'ping -n 1 {ip_address}')  # for linux -c
        if ping_response == 0:
            logging.info(f'{ip_address} is reachable')
            waiting = False
        else:
            time.sleep(1)
            print(f'waiting for host...')
            if datetime.now().strftime("%H:%M:%S") == end_timestamp.strftime("%H:%M:%S"):
                print(f'{os.path.basename(__file__)}: an error has occurred, check logs for more information')
                logging.error(f'Request timed out, {ip_address} did not response to ping in {int((end_timestamp - start_timestamp).total_seconds())} seconds')
                sys.exit(0)


def _get_num_of_backups(dest_dir):  # count number of existing files in destination folder
    return 0
    count = 0
    for directory in os.listdir(dest_dir):
        if os.path.isdir(os.path.join(dest_dir, directory)):
            count += 1
    return int(count)


def _get_today():
    return (datetime.now()).strftime('%Y-%m-%d')


def _get_datetime_object(date):
    return datetime.strptime(date, '%H:%M:%S')


def parse_args():
    arg_parser = argparse.ArgumentParser(description='Backup scripts using rsync-backup to make CRON backups')
    arg_parser.add_argument('-s', '--srcDir', nargs='+', help='Source directory which will be backed up, several directories may be selected in format {-s dir1 dir2 dirN}', type=str, required=True)
    arg_parser.add_argument('-d', '--destDir', help='Destination directory where backup will be stored in format {-d dir}', type=str, required=True)
    arg_parser.add_argument('-H', '--srcHost', help='Specified host if selected dirs are on remote host in format {-H user@address}. Default value is localhost', type=str, default='localhost')
    arg_parser.add_argument('-n', '--numBackup', help='Number of max backup directories, if there will be more than specified number the oldest backup will be deleted, default value is 5', type=int, default=5)
    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    make_backup(args.srcDir, args.destDir, args.srcHost, args.numBackup)

'''
("ping " + ("-n 1 " if  platform.system().lower()=="windows" else "-c 1 ") + host)
/media/logs/backup-tool.log

crontab
0 4 * * 1 ./backup-tool.py -s /home /etc /root /boot /opt -d /var/raid1/sftp/storage-user/backups/system
'''


