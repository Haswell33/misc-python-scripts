#!/usr/bin/env python3

if __name__ == '__main__':
    with open('output.txt', 'w') as f_w:
        f_w.write('')

    with open('hosts.txt', 'r') as f_r:
        for line in f_r.readlines():
            line_split = line.replace('\n', '').split(':')
            host_name = line_split[1]
            host_address = line_split[0]
            with open('output.txt', 'a') as f_w:
                f_w.write(f'Host {host_name}\n')
                f_w.write(f'\tHostname {host_address}\n\n')
