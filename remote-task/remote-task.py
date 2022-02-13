#!/usr/bin/env python3

import logging
import logging.config
import argparse
import sys
import os
import struct
import socket
from termcolor import colored

logging.basicConfig(filename=f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log', format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def start(hostname):  # Wake On Lan packet
    mac_address = get_mac(hostname)
    mac_address = mac_address.replace(mac_address[2], '')
    print(mac_address)
    data = ''.join(['FFFFFFFFFFFF', mac_address * 20])  # pad the synchronization stream.
    send_data = b''
    for i in range(0, len(data), 2):  # split up the hex values and pack.
        send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])
    wol_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # broadcast it to the LAN.
    wol_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    wol_sock.sendto(send_data, ('192.168.0.255', 7))
    logging.debug(f'WOL packet has been sent to {hostname}')
    print(f'WOL packet has been sent to {hostname}')


def stop(hostname):
    system = get_system()
    ip_address = get_ip(hostname)
    user = 'karol.siedlaczek'
    if system == 'win32':
        os.system(f'ssh {user}@{ip_address} "shutdown -s"')
    elif system == 'linux' or system == 'linux2':
        os.system(f'ssh {user}@{ip_address} "shutdown -h"')
    logging.debug(f'{hostname} has been shutdown by logging in to {user} using ssh')
    print(f'{hostname} has been shutdown by logging in to {user} using ssh')


def sleep(hostname):
    system = get_system()
    ip_address = get_ip(hostname)
    user = 'karol.siedlaczek'
    if system == 'win32':
        os.system(f'ssh {user}@{ip_address} "shutdown -h"')
    elif system == 'linux' or system == 'linux2':
        os.system(f'ssh {user}@{ip_address} "systemctl hibernate"')
    logging.debug(f'{hostname} has been asleep by logging in to {user} using ssh')
    print(f'{hostname} has been asleep by logging in to {user} using ssh')


def restart(hostname):
    system = get_system()
    ip_address = get_ip(hostname)
    user = get_user()
    if system == 'win32':
        os.system(f'ssh {user}@{ip_address} "shutdown -r"')
    elif system == 'linux' or system == 'linux2':
        os.system(f'ssh {user}@{ip_address} "reboot"')
    logging.debug(f'{hostname} has been restarted by logging in to {user} using ssh')
    print(f'{hostname} has been restarted by logging in to {user} using ssh')


def get_system():  # windows = win32; linux = linux, linux2
    return sys.platform


def get_list():  # shows lists of available hosts
    print('fun in progress')


def status(hostname):  # just ping to host
    ip_address = get_ip(hostname)
    response = os.popen(f'ping -n 4 {ip_address}').read()  # for linux -c, for windows -n
    if 'Destination host unreachable' in response or 'Request timed out' in response or 'Received = 0' in response:
        print(hostname + ': ' + colored('OFF', 'red'))
    else:
        print(hostname + ': ' + colored('ON', 'green'))


'''
def message(input_host, message):
    #general = CONFIG['GENERAL']
    #ip_address = verify_ip_address(input_host)
    #ip_address = '10.255.4.222'
    #port = general['send_msg_to_host-port']
    #timeout_time = general['send_msg_to_host-timeout_time']
    #host = (ip_address, port)
    #udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #while True:
    #    data = input('Enter message to send or type 'exit': ')
    #    udp_sock.sendto(data, host)
    #    if data == 'exit':
    #        break
    #udp_sock.close()
    #os._exit(0)
    #TCP_IP = '10.255.4.222'
    #TCP_PORT = 5005
    #BUFFER_SIZE = 1024
    #MESSAGE = "Hello, World!"
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect((TCP_IP, TCP_PORT))
    #s.send(MESSAGE)
    #data = s.recv(BUFFER_SIZE)
    #s.close()
    #print("received data:", data)
'''


def get_ip(hostname):  # tmp fun
    if hostname == 'desktop':  # temp solution
        return '192.168.0.101'
    else:
        print('I do not know you, pozniej bedzie baza')
        sys.exit(0)
def get_user():
    return 'karol.siedlaczek'
def get_mac(hostname):
    if hostname == 'desktop':  # temp solution
        return '00:D8:61:9D:D8:1A'
    else:
        print('I do not know you, pozniej bedzie baza')
        sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser(description='Performs predefined operations on specified list of hosts')
    parser.add_argument('-c', '--command', help='Operation type in format {-o operationName}', choices=['start', 'stop', 'restart', 'sleep', 'status', 'list'], type=str, required=True)
    parser.add_argument('-H', '--hostName', help='Hostname from specified list in format {-n hostName}', type=str, required=True)
    # parser.add_argument('-m', '--message', help='message in order to send as popup on specified desktop in format {-m message-text}', type=str, required=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    hostname = args.hostName
    command = args.command
    if command == 'start':
        start(hostname)
    elif command == 'stop':
        stop(hostname)
    elif command == 'restart':
        restart(hostname)
    elif command == 'sleep':
        sleep(hostname)
    elif command == 'status':
        status(hostname)
    elif command == 'list':
        get_list()