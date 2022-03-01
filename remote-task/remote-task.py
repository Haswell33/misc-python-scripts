#!/usr/bin/env python3

import logging
import logging.config
import argparse
import sys
import os
import struct
import socket
import psycopg2
import re
from termcolor import colored

#LOG_FILE = f'/var/log/{os.path.basename(__file__).split(".")[0]}.log'
LOG_FILE = f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log'
PASSWORD_FILE = '/root/.ssh/.password'

logging.basicConfig(filename=LOG_FILE, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def start(hostname):  # Wake On Lan packet
    mac_address = get_mac_address(hostname)
    broadcast = get_broadcast_address(hostname)
    mac_address = mac_address.replace(mac_address[2], '')
    data = ''.join(['FFFFFFFFFFFF', mac_address * 20])  # pad the synchronization stream.
    send_data = b''
    for i in range(0, len(data), 2):  # split up the hex values and pack.
        send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])
    wol_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # broadcast it to the LAN.
    wol_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    wol_sock.sendto(send_data, (broadcast, 7))
    logging.debug(f'{hostname} has been started using WOL packet')
    print(f'{hostname} has been started')


def stop(hostname):
    ip_address = get_ip_address(hostname)
    system = get_system(hostname)
    user = get_ssh_user(hostname)
    if system == 'windows':
        os.system(f'sshpass -P assphrase -f {PASSWORD_FILE} ssh {user}@{ip_address} "shutdown /s"')
    elif system == 'linux':
        os.system(f'sshpass -P assphrase -f {PASSWORD_FILE} ssh {user}@{ip_address} "shutdown -h"')
    logging.debug(f'{hostname} has been shutdown; ssh_user: {user}')
    print(f'{hostname} has been shutdown')


def sleep(hostname):
    ip_address = get_ip_address(hostname)
    system = get_system(hostname)
    user = get_ssh_user(hostname)
    if system == 'windows':
        os.system(f'sshpass -P assphrase -f {PASSWORD_FILE} ssh {user}@{ip_address} "shutdown /h"')
    elif system == 'linux':
        os.system(f'sshpass -P assphrase -f {PASSWORD_FILE} ssh {user}@{ip_address} "systemctl hibernate"')
    logging.debug(f'{hostname} has been asleep; ssh_user: {user}')
    print(f'{hostname} has been asleep')


def restart(hostname):
    ip_address = get_ip_address(hostname)
    system = get_system(hostname)
    user = get_ssh_user(hostname)
    if system == 'windows':
        os.system(f'sshpass -P assphrase -f {PASSWORD_FILE} ssh {user}@{ip_address} "shutdown /r /t 1"')
    elif system == 'linux':
        os.system(f'sshpass -P assphrase -f {PASSWORD_FILE} ssh {user}@{ip_address} "reboot"')
    logging.debug(f'{hostname} has been restarted; ssh_user: {user}')
    print(f'{hostname} has been restarted')


def status(hostname):  # just ping to host
    ip_address = get_ip_address(hostname)
    response = os.popen(f'ping -c 2 {ip_address}').read()  # for linux -c, for windows -n
    if re.search('[Dd]estination [Hh]ost [Uu]nreachable', response) or \
       re.search('[Rr]equest [Tt]imed [Oo]ut', response) or \
       re.search('[Rr]eceived = 0', response) or \
       re.search('0 [Rr]eceived', response):
        print(colored('OFF', 'red') + ' ' + hostname)
        '''user_input = input(f'turn on {hostname}? [Y/n]')
        if user_input == 'Y':
            start(hostname)
        elif user_input == 'n':
            pass
        else:
            user_'''
    else:
        print(colored('ON', 'green') + ' ' + hostname)


def get_db_connection():  # psql database connection
    return psycopg2.connect(host='127.0.0.1', user='haswell', port=5432, password='', database='config')


def get_ip_address(name):
    return send_db_request('ip_address', name)


def get_mac_address(name):
    return send_db_request('mac_address', name)


def get_broadcast_address(name):
    return send_db_request('broadcast', name)


def get_system(name):
    return send_db_request('system', name)


def get_ssh_user(name):
    return send_db_request('ssh_user', name)


def send_db_request(col_name, hostname):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(f"SELECT {col_name} FROM public.hosts WHERE name='{hostname}'")
    results = cursor.fetchone()
    try:
        if results[0] is None or not results:
            print(f'{os.path.basename(__file__)}: an error has occurred, check "{LOG_FILE}" for more information')
            logging.error(f'"{hostname}" has NULL value in "{col_name}" column')
            sys.exit(0)
    except TypeError:
        print(f'{os.path.basename(__file__)}: an error has occurred, check "{LOG_FILE}" for more information')
        logging.error(f'not found hostname "{hostname}" in database')
        sys.exit(0)
    return results[0]


def get_hostname_list():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM public.hosts")
    results = cursor.fetchall()
    print('available hosts:')
    for result in results:
        print(f' - {result[0]}')


def parse_args():
    parser = argparse.ArgumentParser(description='Performs predefined operations on specified list of hosts')
    parser.add_argument('-c', '--command', help='Command in format {-c command}', choices=['start', 'stop', 'restart', 'sleep', 'status'], type=str)
    parser.add_argument('-H', '--hostName', help='Hostname from specified list which is stored on database, format {-H hostname}', type=str)
    parser.add_argument('-l', '--list', help='Get list of available hosts', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.list:
        get_hostname_list()
    if args.command == 'start':
        start(args.hostName)
    elif args.command == 'stop':
        stop(args.hostName)
    elif args.command == 'restart':
        restart(args.hostName)
    elif args.command == 'sleep':
        sleep(args.hostName)
    elif args.command == 'status':
        status(args.hostName)
