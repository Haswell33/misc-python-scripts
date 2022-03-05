#!/usr/bin/env python3

import logging
import logging.config
import argparse
import os
from getpass import getpass

# LOG_FILE = f'/var/log/{os.path.basename(__file__).split(".")[0]}.log'
import subprocess

LOG_FILE = f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log'
USER_TYPE_LIST = {'internal': 'ssh-int',
                  'external': 'ssh-ext'}
INT_USER_CONST = {
    'name': 'internal',
    'group': 'ssh-int',
    'port': '22',
    'dir': '/storage/sftp'
}
EXT_USER_CONST = {
    'name': 'external',
    'group': 'ssh-ext',
    'port': '2222',
    'dir': '/storage/sftp'
}
LOCATION_TYPE_LIST = {'default': '/storage/ssd/sftp',
                      'domain': '/storage/ssd/domain'}
logging.basicConfig(filename=LOG_FILE, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def create_sftp_account():
    print(EXT_USER_CONST.get('title'))
    username = input(f'Enter a username for new SFTP account:\n')
    user_type = input(f'Choose user type (internal or external), for more information {os.path.basename(__file__)} -h:\n')
    while user_type not in [EXT_USER_CONST.get('name'), INT_USER_CONST.get('name')]:
        user_type = input('Choice does not match with available options, choose user type again:\n')
    if user_type == EXT_USER_CONST.get('name'):  # external user type
        password = getpass(prompt='Enter the password: ')
        password_retyped = getpass(prompt='Retype password: ')
        while password != password_retyped:
            print('Password does not match. Try again')
            password = getpass(prompt='Enter the password: ')
            password_retyped = getpass(prompt='Retype password: ')
        print(f'useradd -M --shell /bin/false -p {password} -G {EXT_USER_CONST.get("group")},sftp-users {username}')
        print(f'mkdir -p ')


def remove_sftp_account():
    pass


def get_sftp_users_list():
    # ext_output = 'ssh-ext:x:1006:keepass,karol_siedlaczek'
    ext_output = str(subprocess.Popen(f'cat /etc/group | grep "{EXT_USER_CONST.get("group")}"', shell=True))
    # int_output = 'ssh-int:x:1007:root,storage'
    int_output = str(subprocess.Popen(f'cat /etc/group | grep "{INT_USER_CONST.get("group")}"', shell=True))
    ext_users = (ext_output.rsplit(':', 1)[-1]).split(',')
    int_users = (int_output.rsplit(':', 1)[-1]).split(',')
    print('name\t\t\ttype\t\t\tlisten_port')
    for user in ext_users:
        print(f'{user}\t\t\t{EXT_USER_CONST.get("title")}\t\t\t{EXT_USER_CONST.get("port")}')
    for user in int_users:
        print(f'{user}\t\t\t{INT_USER_CONST.get("title")}\t\t\t{INT_USER_CONST.get("port")}')


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-a', '--addUser', help='', action='store_true')
    parser.add_argument('-r', '--removeUser', help='', action='store_true')
    parser.add_argument('-t', '--userType', help='Internal account type will listen on port 2222 and allows to access using password without pubkey. '
                                                  'External account type will listen on port 22 and allows to access using only pubkey', choices=['ext', 'int'])
    parser.add_argument('-d', '--domain', help='', action='store_true', default=False)
    parser.add_argument('-l', '--list', help='Get list of currently configured sftp accounts', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.addUser:
        create_sftp_account(args.domain)
    elif args.removeUser:
        remove_sftp_account()
    elif args.list:
        get_sftp_users_list()