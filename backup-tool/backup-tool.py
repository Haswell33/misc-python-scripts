#!/usr/bin/env python3

import os
import re
import sys
import time
import shutil
import logging
import argparse
from getpass import getpass
from ipaddress import ip_address
from datetime import datetime
from dateutil.relativedelta import relativedelta

DEFAULTS = {
    'HOST_ADDRESS': ip_address('127.0.0.1'),
    'LOG_FILE': f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log',
    'RUN_USER': 'storage',
    'MAX': 10  # max number of backups, if max number will be exceeded the oldest file backup be deleted
}

# 'MOUNT_POINT': '/storage/raid1',
# 'PASSWORD_FILE': '/root/.ssh/.password',

logging.basicConfig(filename=DEFAULTS['LOG_FILE'], format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def create_backup(file_backup, db_backup, host_address, user, password, source_dirs, dest_dir, db_port, databases, max, run_user):
    timestamp = datetime.now().strftime('%Y%m%d%H%M.%S')

    if file_backup:
        backup_file = f'{dest_dir}/backup-{get_today()}'  # dest directory where backup files will be stored
        logging.info(f'backup "{backup_file}" in progress, source dirs: "{", ".join(f"{host_address}:{directory}" for directory in source_dirs)}"')
        cmd = get_file_backup_cmd(file_backup, host_address, user, password, source_dirs, backup_file)
    elif db_backup:
        logging.info(f'backup "{backup_file}" in progress, databases: "{", ".join(f"{host_address}:{database}" for database in databases)}"')
        cmd = get_db_backup_cmd(db_backup, host_address, user, password, databases, db_port, dest_dir)
    logging.debug(f'rsync command to run: "{cmd}"')
    if get_backups_num(dest_dir) > max:  # if number of backups in dest directory is greater than defined max number - the oldest will be deleted
        remove_oldest_backup(dest_dir, max)


    #cmd = get_cmd(ssh, daemon, host_address, user, password, source_dirs, backup_file)  # rsync command
    # os.system(f'su {run_user} -c "{cmd} --info=progress2 > {backup_file}/rsync.log"')
    # os.system(f'su {run_user} -c "touch -t {curr_timestamp}"')
    logging.info(f'backup "{backup_file}" completed')


def get_file_backup_cmd(backup_type, host, user, password, source_dirs, backup_file):
    if backup_type == 'ssh':  # -l to copy links, -v verbosity in log, -t timestamps in log, -a archive mode, so recurse mode is on
        source_dirs = ' '.join(f'{host}:{directory}' for directory in source_dirs)
        return f'rsync -altv --rsh="sshpass -P assphrase -p {password} ssh -l {user}" {source_dirs} {backup_file}'
    elif backup_type == 'daemon':
        source_dirs = ' '.join(f'rsync://{user}@{host}{directory}' for directory in source_dirs)
        return f'RSYNC_PASSWORD={password} rsync -altv {source_dirs} {backup_file}'
    else:  # from local path
        source_dirs = ' '.join(directory for directory in source_dirs[:-1])
        return f'rsync -altv {source_dirs} {backup_file}'


def get_db_backup_cmd(backup_type, db_host, db_user, db_password, databases, db_port, dest_dir):
    commands = []
    today = get_today()
    if backup_type == 'psql':
        for database in databases:  # -F t to .tar format
            commands.append(f'pg_dump -h {db_host} -p {db_port} -U {db_user} -F t {database} > {dest_dir}/{database}/{database}-{today}.sql.tar')
    elif backup_type == 'mysql':
        for database in databases:
            commands.append(f'mysqldump -h {db_host } --port {db_port } -u {db_user} -p {db_password} {database} > {dest_dir}/{database}/{database}-{today}.sql.tar')
    return commands


def get_backups_num(directory):  # count number of existing files in destination folder
    try:
        count = 0
        backups = os.listdir(directory)
        for backup in backups:
            if os.path.isdir(os.path.join(directory, backup)):
                count += 1
        return int(count)
    except FileNotFoundError:
        return 0  # no parent directory for backups means no backup


def remove_oldest_backup(dest_dir, max):
    os.chdir(dest_dir)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)  # files[0] is the oldest file, files[-1] is the newest
    for file in files:
        if os.path.isdir(file):  # looking for first dir in array, so it will find the oldest dir
            oldest_backup = file
            break
    try:
        regex_pattern = r'^backup-\d{4}-\d{2}-\d{2}'  # to avoid deleting unexpected directory when user provide wrong path
        if re.match(regex_pattern, oldest_backup):
            logging.info(f'max num of backups exceeded, current amount is greater than {max}, deleting oldest backup "{dest_dir}/{oldest_backup}" in progress...')
            shutil.rmtree(f'{dest_dir}/{oldest_backup}')
            logging.debug(f'oldest backup "{dest_dir}/{oldest_backup}" has been deleted')
        else:
            logging.warning(f'directory not deleted, name of "{dest_dir}/{oldest_backup}" is not usual for backup filename')
    except PermissionError as e:
        logging.error(f'{os.path.basename(__file__)}: {e}, cannot delete oldest backup "{oldest_backup}"')
        print(f'{os.path.basename(__file__)}: an error has occurred, check {DEFAULTS["LOG_FILE"]} for more information')


def host_is_up(host_address, timeout):
    start_timestamp = get_datetime_object(datetime.now().strftime('%H:%M:%S'))
    end_timestamp = start_timestamp + relativedelta(seconds=+timeout)  # setting up timeout
    waiting = True
    logging.info(f'checking if {host_address} is up...')
    while waiting:
        response = os.popen(f'ping -c 1 {host_address}').read()  # for linux -c, for windows -n
        if re.search('[Dd]estination [Hh]ost [Uu]nreachable', response) or \
           re.search('[Rr]equest [Tt]imed [Oo]ut', response) or \
           re.search('[Rr]eceived = 0', response) or \
           re.search('0 [Rr]eceived', response):
            time.sleep(1)
            print(f'waiting for {host_address}...')
            if datetime.now().strftime("%H:%M:%S") >= end_timestamp.strftime("%H:%M:%S"):
                print(f'{os.path.basename(__file__)}: an error has occurred, check {DEFAULTS["LOG_FILE"]} for more information')
                logging.error(f'Request timed out, {host_address} did not response to ping in {int((end_timestamp - start_timestamp).total_seconds())} seconds')
                return False
        else:
            logging.info(f'{ip_address} is up')
            waiting = False
    return True


def start_host(host_address):
    os.system(f'/usr/local/bin/remote-task.py -c start -H {host_address}')
    logging.info(f'WOL packet has been sent to {host_address} to turn on host')
    host_is_up(ip_address, 120)

'''
def check_if_md0_mounted():
    response = os.popen(f'mountpoint {MOUNT_POINT}')
    if 'not a mountpoint' in response:
        logging.error(f'{MOUNT_POINT} not mounted, backup creation aborted')
        sys.exit(0)
'''


def get_today():
    return (datetime.now()).strftime('%Y-%m-%d')


def get_datetime_object(date):
    return datetime.strptime(date, '%H:%M:%S')


def parse_args():
    parser = argparse.ArgumentParser(description='Script which using rsync-backup to make backups. It is rsync with --archive mode, but with some additionally functions')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file',
                       choices=['ssh', 'daemon'],
                       help='Type of rsync connection')
    group.add_argument('--database',
                       choices=['mysql', 'psql'],
                       help='Type of database to dump')
    parser.add_argument('--prompt',
                        action='store_true',
                        help='arg to force password prompt')
    parser.add_argument('-D', '--dbNames',
                        nargs='+',
                        help='Databases name to backup, only usable when --database backup',
                        type=str,
                        required='--database' in sys.argv)
    parser.add_argument('-P', '--dbPort',
                        help='Database port, only usable when --database backup',
                        type=int,
                        required='--database' in sys.argv)
    parser.add_argument('-s', '--sourceDirs',
                        nargs='+',
                        help='Directories',
                        required='--file' in sys.argv)
    parser.add_argument('-d', '--destDir',
                        help='',
                        type=str,
                        required=True)
    parser.add_argument('--runUser',
                        help=f'User which locally runs script, default is "{DEFAULTS["RUN_USER"]}"',
                        type=str,
                        default=DEFAULTS['RUN_USER'])
    parser.add_argument('-H', '--hostAddress',
                        help=f'host address where files are stored, default is {DEFAULTS["HOST_ADDRESS"]}',
                        type=ip_address,
                        default=DEFAULTS['HOST_ADDRESS'])
    parser.add_argument('-u', '--user',
                        help='User to establish remote connection',
                        type=str,
                        required='--database' in sys.argv)
    parser.add_argument('-p', '--password',
                        help='',
                        type=str,
                        required='--prompt' not in sys.argv)
    parser.add_argument('-m', '--max',
                        help=f'Number of max backup directories, if there will be more than specified number the oldest backup will be deleted, default is {DEFAULTS["MAX"]}',
                        type=int,
                        default=DEFAULTS['MAX'])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        if args.hostAddress is not DEFAULTS['HOST_ADDRESS'] and args.user is None:  # files are on remote host and user is not given
            raise ValueError(f'-u/--user arg expected to establish remote connection with {args.hostAddress}')
        elif args.prompt:
            args.password = getpass(prompt=f'Enter password for user "{args.user}": ')
        create_backup(args.file, args.database, args.hostAddress, args.user, args.password, args.sourceDirs, args.destDir, args.dbPort, args.dbNames, args.max, args.runUser)
    except ValueError as e:
        logging.error(f'{os.path.basename(__file__)}: {e}')
        print(f'{os.path.basename(__file__)}: {e}')

    '''
    
    def get_cmd(ssh, daemon, host_address, user, password, source_dirs, backup_file):
    if ssh:  # -l to copy links, -v verbosity in log, -t timestamps in log, -a archive mode, so recurse mode is on
        source_dirs = ' '.join(f'{host_address}:{directory}' for directory in source_dirs)
        cmd = f'rsync -altv --rsh="sshpass -P assphrase -p {password} ssh -l {user}" {source_dirs} {backup_file}'
    elif daemon:
        source_dirs = ' '.join(f'rsync://{user}@{host_address}{directory}' for directory in source_dirs)
        cmd = f'RSYNC_PASSWORD={password} rsync -altv {source_dirs} {backup_file}'
    else:  # backup from local path
        source_dirs = ' '.join(directory for directory in source_dirs[:-1])
        cmd = f'rsync -altv {source_dirs} {backup_file}'
    #cmd += f' --info=progress2 > {backup_file}/rsync.log'  # to get output into log file
    return cmd
    
            if len(args.dirs) < 2:
            raise ValueError('expected more values in -d/--dirs argument, minimum value is at least 2 directories')
    if ssh_conn:
        cmd = 
        pass
    elif daemon_conn:
        pass
    elif local_conn:
        pass

    regex_pattern = r'^(\d{3}.\d{3}.\d{1}.\d{2,3})'
    curr_timestamp = datetime.now().strftime('%Y%m%d%H%M.%S')
    ssh_conn = False
    dest_dir = directories[-1]
    # check_if_md0_mounted()
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
    if not re.match(regex_pattern, dest_dir):
        if get_num_of_backups(dest_dir) > max_num_of_backups:
            logging.info(f'num of backups exceeded, current amount is greater than {max_num_of_backups}, oldest backup will be deleted')
            remove_oldest_backup(dest_dir)
    else:
        logging.info('checking num of backups skipped, destination directory is remote host')
    send_rsync(directories, user, ssh_conn)
    logging.debug(f'backup complete "{dest_dir}/{backup_filename}"')
    os.system(f'chown -R {STORAGE_USER} {dest_dir}/{backup_filename}')
    os.system(f'touch -t {curr_timestamp} {dest_dir}/{backup_filename}')  # change mtime on backup creation date
    '''