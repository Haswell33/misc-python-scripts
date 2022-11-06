#!/usr/bin/env python3

import logging
import logging.config
import argparse
import sys
import os
import time
import struct
import socket
import ipaddress
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

PASSWORD_FILE = '/root/.ssh/.password'

DEFAULTS = {
    'HOSTS_FILE': os.path.abspath(os.path.join(os.sep, 'etc', 'hosts')),
    'LOG_FILE': f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log',
    #'LOG_FILE': os.path.abspath(os.path.join(os.sep, 'var', 'log', f'{os.path.basename(__file__).split(".")[0]}.log')),
}

logging.basicConfig(filename=DEFAULTS['LOG_FILE'], format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


class Host:
    network = 'eth0'
    ip_address_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    mac_address_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

    def __init__(self, host_address, hosts_file=DEFAULTS['HOSTS_FILE']):
        self.ip_address = host_address
        self.hosts_file = hosts_file
        self.name = None
        self.mac_address = None
        self.broadcast = None

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def name(self):
        return self._name

    @property
    def mac_address(self):
        return self._mac_address

    @property
    def broadcast(self):
        return self._broadcast

    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = None

    @name.setter
    def name(self, value):
        try:
            hosts = open(self.hosts_file, 'r')
            for host in hosts:
                try:
                    ip_address = host.split()[0]
                    hostname = host.split()[-1]
                    if ip_address == str(self.ip_address):
                        self._name = hostname
                except IndexError:
                    pass
        except FileNotFoundError as e:
            logging.warning(f'{os.path.basename(__file__)}: {e}, define this file as --hostsFile or create')
            self._name = None

    @mac_address.setter
    def mac_address(self, value):
        ip_neigh = os.popen(f'ip neigh show {self.ip_address}').read().split()
        if ip_neigh:
            for line in ip_neigh:
                if re.match(self.mac_address_pattern, line):
                    self._mac_address = line
        else:
            self._mac_address = None

    @broadcast.setter
    def broadcast(self, value):
        if self.mac_address is None:  # host not found in ip neigh, abort setting broadcast
            self._broadcast = None
        else:
            ip_addr = os.popen(f'ip -4 addr show {self.network} | grep inet').read().split()  # linux usage
            for index, line in enumerate(ip_addr):
                if re.match(self.ip_address_pattern, line) and ip_addr[index - 1] == 'brd':
                    self._broadcast = line

    def start(self):
        mac_address = self.mac_address.replace(self.mac_address[2], '')
        data = ''.join(['FFFFFFFFFFFF', mac_address * 20])  # pad the synchronization stream.
        send_data = b''
        for i in range(0, len(data), 2):  # split up the hex values and pack.
            send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])
        wol_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # broadcast it to the LAN.
        wol_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        wol_sock.sendto(send_data, (self.broadcast, 7))
        logging.debug(f'WOL packet has been sent to "{self}" to turn on host')
        print(f'WOL packet has been sent to "{self}" to turn on host')

    def is_up(self, timeout):
        start_timestamp = datetime.strptime(datetime.now().strftime('%H:%M:%S'), '%H:%M:%S')
        end_timestamp = start_timestamp + relativedelta(seconds=+timeout)  # setting up timeout
        waiting = True
        logging.info(f'checking if "{self}" is up...')
        while waiting:
            response = os.popen(f'ping -c 1 {self}').read()  # for linux -c, for windows -n
            if re.search('[Dd]estination [Hh]ost [Uu]nreachable', response) or \
                    re.search('[Rr]equest [Tt]imed [Oo]ut', response) or \
                    re.search('[Rr]eceived = 0', response) or \
                    re.search('0 [Rr]eceived', response):
                time.sleep(1)
                print(f'waiting for {self}...')
                if datetime.now().strftime("%H:%M:%S") >= end_timestamp.strftime("%H:%M:%S"):
                    logging.error(f'Request timed out, {self} did not response to ping in {int((end_timestamp - start_timestamp).total_seconds())} seconds')
                    return False
            else:
                logging.info(f'host "{self}" is up')
                waiting = False
        return True

    def __str__(self):
        if self.name is None:
            return str(self.ip_address)
        else:
            return self.name


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


def parse_args():
    parser = argparse.ArgumentParser(description='Performs predefined operations on specified list of hosts')
    parser.add_argument('-c', '--command', help='Command in format {-c command}', choices=['start', 'stop', 'restart', 'sleep', 'status'], type=str)
    parser.add_argument('-H', '--host', help='Hostname from specified list which is stored on database, format {-H hostname}', type=str)
    parser.add_argument('-l', '--list', help='Get list of available hosts', action='store_true')
    parser.add_argument('--hostsFile',
                        help=f'File with hosts, default is {DEFAULTS["HOSTS_FILE"]}',
                        type=str,
                        metavar='file',
                        default=DEFAULTS['HOSTS_FILE'])
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    host = Host(args.host, args.hostsFile)
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
