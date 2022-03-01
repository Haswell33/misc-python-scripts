#!/usr/bin/env python3

import os
import re
import sys
import time
import shutil
import logging
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta

LOG_FILE = f'/var/log/{os.path.basename(__file__).split(".")[0]}.log'
# LOG_FILE = f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log'
PASSWORD_FILE = '/root/.ssh/.password'
STORAGE_USER = 'storage'

logging.basicConfig(filename=LOG_FILE, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def make_backup(directories, user, max_num_of_backups):
    regex_pattern = r'^(\d{3}.\d{3}.\d{1}.\d{2,3})'
    ssh_conn = False
    dest_dir = directories[-1]
    backup_filename = f'backup-{_get_today()}'
    directories[-1] += '/' + backup_filename
    logging.debug(f'backup in progress "{dest_dir}/{backup_filename}"...')
    os.system(f'mkdir -p {directories[-1]}')
    for directory in directories:
        if re.findall(regex_pattern, directory):  # means that rsync will need to work via ssh with other host, because found ip address in provided dir
            if not user:
                print(f'{os.path.basename(__file__)}: -u/--user arg expected if remote connection, backup creation aborted')
                logging.error(f'-u/--user arg expected if remote connection, backup creation aborted')
                sys.exit(0)
            ip_address = re.findall(regex_pattern, directory)[0]
            if not host_is_up(ip_address, 10):
                start_host(ip_address)
            ssh_conn = True
            break
    send_rsync(directories, user, ssh_conn)
    logging.debug(f'backup complete "{dest_dir}/{backup_filename}"')
    if not re.match(regex_pattern, dest_dir):
        if _get_num_of_backups(dest_dir) > max_num_of_backups:
            logging.info(f'num of backups exceeded, current amount is greater than {max_num_of_backups}, oldest backup will be deleted')
            remove_oldest_backup(dest_dir)
    else:
        logging.info('checking num of backups skipped, destination directory is remote host')
    os.system(f'chown -R {STORAGE_USER} {dest_dir}/{backup_filename}')


def send_rsync(dirs, user, ssh_conn):
    rsync_args = ''
    for directory in dirs:
        rsync_args += directory + ' '
    if ssh_conn:  # remote connection
        os.system(f'rsync -altv --rsh="sshpass -P assphrase -f {PASSWORD_FILE} ssh -l {user}" {rsync_args}--info=progress2 > {dirs[-1]}/rsync.log')
    else:  # local connection
        os.system(f'rsync -altv {rsync_args}--info=progress2 > {dirs[-1]}/rsync.log')


def remove_oldest_backup(dest_dir):
    regex_pattern = r'^backup-\d{4}-\d{2}-\d{2}'  # to avoid deleting unexpected directory when user provide wrong path
    os.chdir(dest_dir)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)  # files[0] is the oldest file, files[-1] is the newest
    for file in files:
        if os.path.isdir(file):  # looking for first dir in array, so it will find the oldest dir
            oldest_backup = file
            break
    try:
        if re.match(regex_pattern, oldest_backup):
            logging.info(f'oldest backup deleting in progress "{dest_dir}/{oldest_backup}"...')
            shutil.rmtree(f'{dest_dir}/{oldest_backup}')
            logging.debug(f'oldest backup deleted "{dest_dir}/{oldest_backup}"')
        else:
            logging.warning(f'directory not deleted, name of "{dest_dir}/{oldest_backup}" is not usual for backup filename')
    except PermissionError as error_msg:
        logging.error(f'PermissionError: {str(error_msg)}, can not delete oldest backup directory')
        print(f'{os.path.basename(__file__)}: an error has occurred, check {LOG_FILE} for more information')
        return


def host_is_up(ip_address, timeout):
    start_timestamp = _get_datetime_object(datetime.now().strftime('%H:%M:%S'))
    end_timestamp = start_timestamp + relativedelta(seconds=+timeout)  # setting up timeout
    waiting = True
    logging.info('checking if host is up...')
    while waiting:
        response = os.popen(f'ping -c 1 {ip_address}').read()  # for linux -c, for windows -n
        if re.search('[Dd]estination [Hh]ost [Uu]nreachable', response) or \
           re.search('[Rr]equest [Tt]imed [Oo]ut', response) or \
           re.search('[Rr]eceived = 0', response) or \
           re.search('0 [Rr]eceived', response):
            time.sleep(1)
            print(f'waiting for host...')
            if datetime.now().strftime("%H:%M:%S") >= end_timestamp.strftime("%H:%M:%S"):
                print(f'{os.path.basename(__file__)}: an error has occurred, check {LOG_FILE} for more information')
                logging.error(f'Request timed out, {ip_address} did not response to ping in {int((end_timestamp - start_timestamp).total_seconds())} seconds')
                return False
        else:
            logging.info(f'{ip_address} is up')
            waiting = False
    return True


def start_host(ip_address):
    os.system(f'/usr/local/bin/remote-task.py -c start -H desktop')
    logging.info(f'WOL packet has been sent to {ip_address} to turn on host')
    host_is_up(ip_address, 120)


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
    arg_parser = argparse.ArgumentParser(description='Script which using rsync-backup to make backups. It is rsync with --archive mode, but with some additionally functions')
    arg_parser.add_argument('-u', '--user', help='User to establish remote connection via ssh. Need to used if -d/--dirs argument has at least one remote directory', type=str)
    arg_parser.add_argument('-d', '--dirs', nargs='+', help='Argument to specify source directories and one target directory, last one entered will be target directory. '
                                                            'For example if you enter: {-d dir1 dir2 dir3} script (actually rsync) will read data from dir1, dir2 and save it to dir3.'
                                                            'Rsync is enabled to --archive mode, so all data recursively will be copied. It is necessary to provide at least 2 directories. '
                                                            'If you want provide remote directory, type it in format {-d ip_address:dirs} and user by -u/--user argument', type=str, required=True)
    arg_parser.add_argument('-n', '--numBackup', help='Number of max backup directories, if there will be more than specified number the oldest backup will be deleted, default value is 5', type=int, default=5)
    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if len(args.dirs) < 2:
        print(f'{os.path.basename(__file__)}: expected more values in -d/--dirs argument, minimum value is at least 2 directories ')
        sys.exit(0)
    make_backup(args.dirs, args.user, args.numBackup)

