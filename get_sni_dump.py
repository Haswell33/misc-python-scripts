#!/usr/bin/env python3

import json
import argparse
import subprocess

DELIMITER = ';'
FILENAME = 'sni.csv'
NOT_FOUND_FILENAME = 'not_found_addr.csv'
PROJECTS = ['sdp', 'vdp', 'common']


class ServerNameIndication:
    def __init__(self, project, address, subnet_id):
        self.hostname = get_hostname_by_address(address, project)
        self.data_center = self.hostname.split('-')[0]
        self.address = address
        subnet = get_subnet(subnet_id)
        self.subnet_address = subnet['cidr'].split('/')[0]
        self.subnet_size = subnet['cidr'].split('/')[-1]
        if subnet['gateway_ip']:
            self.gateway = subnet['gateway_ip']
        else:
            subnet_per_octet = self.subnet_address.split('.')
            subnet_fourth_octet = subnet_per_octet.pop()
            self.gateway = f'{".".join(subnet_per_octet)}.{int(subnet_fourth_octet) + 1}'  # first address in network
        network = get_network(subnet['network_id'])
        self.vlan = network['provider:segmentation_id']
        self.network_name = network['name']

    def save_to_csv(self, filename):
        with open(filename, 'a') as f:
            f.write(f'{self.data_center}{DELIMITER}'
                    f'{self.hostname}{DELIMITER}'
                    f'{self.address}{DELIMITER}'
                    f'{self.subnet_address}{DELIMITER}'
                    f'/{self.subnet_size}{DELIMITER}'
                    f'{self.gateway}{DELIMITER}'
                    f'{self.vlan}{DELIMITER}'
                    f'{self.network_name}\n')

    def __str__(self):
        return self.address


def get_subnet(subnet_id):
    return json.loads(run_command(f'openstack subnet show {subnet_id} -f json'))


def get_network(network_id):
    return json.loads(run_command(f'openstack network show {network_id} -f json'))


def get_ports(project):
    return json.loads(run_command(f'openstack port list --project {project} -f json'))


def get_hostname_by_address(address, project):
    try:
        return json.loads(run_command(f'openstack server list --ip {address} --project "{project}" -f json'))[0]['Name']
    except IndexError:
        raise AttributeError(f'Cannot find host with {address} ip address')


def run_command(command):
    process = subprocess.run(command, stdin=subprocess.DEVNULL, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    output = process.stderr if process.stderr else process.stdout
    return output.decode('utf-8').replace('\n', ' ')


def save_not_found_address(filename, ip_address):
    with open(filename, 'a') as f:
        f.write(f'{ip_address}\n')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--projects', nargs='+', default=PROJECTS)
    parser.add_argument('--resetFile', action='store_true')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.resetFile:
        with open(FILENAME, 'w') as f:
            f.write('')
        with open(NOT_FOUND_FILENAME, 'w') as f:
            f.write('')

    for project in args.projects:
        print(f'Start iteration on {project} project')
        for port in get_ports(project):
            ip_address = port['Fixed IP Addresses'][0]['ip_address']
            subnet_id = port['Fixed IP Addresses'][0]['subnet_id']
            try:
                sni = ServerNameIndication(project, ip_address, subnet_id)
                print(f'Found {sni} as {sni.hostname}')
                sni.save_to_csv(FILENAME)
            except AttributeError as e:
                print(e)
                save_not_found_address(NOT_FOUND_FILENAME, ip_address)

