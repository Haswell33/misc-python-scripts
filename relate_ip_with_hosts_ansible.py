import re

if __name__ == '__main__':
    hosts = []
    with open('hosts.txt', 'r') as hosts_file:
        for line in hosts_file.readlines():
            if 'ansible_host' in line:
                hosts.append(line.strip())
    with open('output.txt', 'w') as f_w:
        with open('ok_list.txt', 'r') as file:
            for line in file.readlines():
                for host_line in hosts:
                    hostname = re.search("([a-zA-Z0-9\-]*)\s", host_line.lower()).group(1)
                    hostname_src = re.search("([a-zA-Z0-9\-]*)\s", line.strip().lower()).group(1)
                    if hostname_src == hostname:
                        print(f'{hostname_src};{re.search("ansible_host=([0-9.]*)", host_line).group(1)}')
                        f_w.write(f'{hostname_src};{re.search("ansible_host=([0-9.]*)", host_line).group(1)}\n')