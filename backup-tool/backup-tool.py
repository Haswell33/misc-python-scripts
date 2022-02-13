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
from termcolor import colored

logging.basicConfig(filename=f'{os.path.abspath(os.path.dirname(__file__))}/logs/backup-tool.log', format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

# RSYNC_DESKTOP_PASS = 'testpass'


def make_backup(dirs, max_num_of_backups):
    regex_pattern = r'^\S*@(\d{3}.\d{3}.\d{1}.\d*)'
    dest_dir = dirs[-1]
    backup_filename = f'backup-{_get_today()}'
    dirs[-1] += '/' + backup_filename
    ip_address = re.findall(regex_pattern, dest_dir)[0]
    if ip_address:  # means that rsync will need to work via ssh with other host, because found ip address in provided dir
        if not host_is_up(ip_address, 10):
            start_host(ip_address)
    logging.debug(f'creating backup in progress "{dest_dir}/{backup_filename}"...')
    send_rsync(dirs)
    if not re.match(regex_pattern, dest_dir):
        if _get_num_of_backups(dest_dir) >= max_num_of_backups:
            logging.info(f'number of backups has been exceeded, current amount is greater than {max_num_of_backups}, the oldest directory will be deleted')
            remove_oldest_backup(dest_dir)
    else:
        logging.info('checking num of backups skipped, because destination directory is on remote host')
    logging.debug(f'creating backup "{dest_dir}/{backup_filename}" completed successfully')


def send_rsync(dirs):
    rsync_args = ''
    for directory in dirs:
        rsync_args += directory + ' '
    # print(f'rsync -a {rsync_args}')


def remove_oldest_backup(dest_dir):
    regex_pattern = r'^backup-\d{4}-\d{2}-\d{2}'  # to avoid deleting unexpected directory when user provide wrong path
    os.chdir(dest_dir)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)  # files[0] is the oldest file, files[-1] is the newest
    for file in files:
        if os.path.isdir(file):  # looking for first dir in array, so it will find the oldest dir
            oldest_backup = file
            break
    try:
        logging.info(f'oldest backup: "{dest_dir}/{oldest_backup}"')
        if re.match(regex_pattern, oldest_backup):
            logging.info(f'deleting oldest backup in progress "{dest_dir}/{oldest_backup}"...')
            # shutil.rmtree(f'{dest_dir}/{oldest_backup}')
            logging.debug(f'deleting oldest backup "{dest_dir}/{oldest_backup}" completed successfully')
        else:
            logging.warning('directory did not deleted, name of directory is not usual for backup filename')
    except PermissionError as error_msg:
        logging.error(f'PermissionError: {str(error_msg)}, can not delete oldest backup directory')
        print(f'{os.path.basename(__file__)}: an error has occurred, check logs for more information')
        return


def host_is_up(ip_address, timeout):
    start_timestamp = _get_datetime_object(datetime.now().strftime('%H:%M:%S'))
    # end_timestamp = start_timestamp + relativedelta(minutes=+1)  # setting up timeout for 120 seconds
    end_timestamp = start_timestamp + relativedelta(seconds=+timeout)  # setting up timeout for 120 seconds
    waiting = True

    while waiting:
        response = os.popen(f'ping -n 1 {ip_address}').read()  # for linux -c, for windows -n
        if 'Destination host unreachable' in response or 'Request timed out' in response or 'Received = 0' in response:
            time.sleep(1)
            print(f'waiting for host...')
            if datetime.now().strftime("%H:%M:%S") == end_timestamp.strftime("%H:%M:%S"):
                print(f'{os.path.basename(__file__)}: an error has occurred, check logs for more information')
                logging.error(f'Request timed out, {ip_address} did not response to ping in {int((end_timestamp - start_timestamp).total_seconds())} seconds')
                # sys.exit(0)
                return False
        else:
            print(f'{ip_address} is up')
            print(ip_address + ': ' + '\033[92m')
            logging.info(f'{ip_address} is up')
            waiting = False
    return True


def start_host(ip_address):
    # os.system(f'./remote-task.py -o start -H desktop')
    # host_is_up(ip_address, 120)
    print(f'WOL packet has been sent to {ip_address} to turn on host')


def _get_num_of_backups(dest_dir):  # count number of existing files in destination folder
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
    arg_parser.add_argument('-d', '--dirs', nargs='+', help='Dirs to specify source and destination directories, last provided dir is destination, for instance {-d dir1 dir2 dir3} will read dir1, dir2 and save in dir3', type=str, required=True)
    arg_parser.add_argument('-n', '--numBackup', help='Number of max backup directories, if there will be more than specified number the oldest backup will be deleted, default value is 5', type=int, default=5)
    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    make_backup(args.dirs, args.numBackup)

'''
("ping " + ("-n 1 " if  platform.system().lower()=="windows" else "-c 1 ") + host)
/media/logs/backup-tool.log

crontab
0 4 * * 1 ./backup-tool.py -s /home /etc /root /boot /opt -d /var/raid1/sftp/storage-user/backups/system
'''


