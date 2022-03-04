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
LOCATION_TYPE_LIST = {'default': '/storage/ssd/sftp',
                      'domain': '/storage/ssd/domain'}
logging.basicConfig(filename=LOG_FILE, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def create_sftp_account():
    #subprocess.Popen('dir', shell=True)
    username = input(f'Enter a username for new SFTP account:\n ')
    user_type = input(f'Choose account type (internal or external), for more information {os.path.basename(__file__)} -h:\n ')

    while user_type not in USER_TYPE_LIST:
        user_type = input('Choice does not match with available options, choose user type again:\n ')
    if user_type == USER_TYPE_LIST[1]:  # external user type
        password = getpass(prompt='Enter the password: ')
        password_retyped = getpass(prompt='Retype password: ')
        while password != password_retyped:
            print('Password does not match. Try again')
            password = getpass(prompt='Enter the password: ')
            password_retyped = getpass(prompt='Retype password: ')


    #subprocess.Popen('adduser')


def remove_sftp_account():
    pass


def get_sftp_users_list():
    ext_list = 'ssh-ext:x:1006:keepass,karol_siedlaczek'
    int_list = 'ssh-int:x:1007:root,storage'
    external_users = []
    internal_users = []
    print('external sftp account:')
    (ext_list.rsplit(':', 1)[-1]).replace(',', '\n')
    print('internal sftp account:')
    print((int_list.rsplit(':', 1)[-1]).replace(',', '\n'))
    # user_list = subprocess.Popen(f'cat /etc/group | grep "{USER_TYPE_LIST.get("internal")}\|{USER_TYPE_LIST.get("external")}"', shell=True)


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-a', '--addUser', help='', action='store_true')
    parser.add_argument('-r', '--removeUser', help='', action='store_true')
    parser.add_argument('-t', '--userType', help='Internal account type will listen on port 2222 and allows to access using password without pubkey. '
                                                  'External account type will listen on port 22 and allows to access using only pubkey', choices=['ext', 'int'])
    parser.add_argument('-l', '--list', help='Get list of currently configured sftp accounts', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.addUser:
        create_sftp_account()
    elif args.removeUser:
        remove_sftp_account()
    elif args.list:
        get_sftp_users_list()