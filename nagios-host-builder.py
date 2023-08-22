#!/usr/bin/env python3

if __name__ == '__main__':
    filename = 'hosts.txt'
    host_group_name = 'redir-hosts'
    members = []
    with open('output.txt', 'w') as f_w:
        f_w.write('')
    with open(filename, 'r') as f_r:
        for line in f_r.readlines():
            line_split = line.replace('\n', '').split(':')
            host_name = line_split[0]
            host_address = line_split[1]
            with open('output.txt', 'a') as f_w:
                f_w.write('define host {\n')
                f_w.write(f'\thost_name\t{host_name.lower()}\n')
                f_w.write(f'\taddress\t\t{host_address}\n')
                f_w.write(f'\tuse\t\t\tgeneric-host\n')
                f_w.write('}\n\n')
            members.append(host_name.lower())
    print(','.join(members))
    with open('output.txt', 'a') as f_w:
        f_w.write('define hostgroup {\n')
        f_w.write(f'\thostgroup_name\t{host_group_name}\n')
        string_members = ",".join(members)
        f_w.write(f'\tmembers\t\t\t{string_members}\n')
        f_w.write('}')
