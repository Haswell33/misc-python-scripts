import re

if __name__ == '__main__':
    with open('not_ok_list.txt', 'w') as f_w:
        f_w.write('')
    with open('ok_list.txt', 'w') as f_w:
        f_w.write('')
    with open('hosts.txt', 'r') as hosts_file:
        for line in hosts_file.readlines():
            if 'failed=1' in line or 'unreachable=1' in line:
                with open('not_ok_list.txt', 'a') as f:
                    f.write(f'{line.strip()}\n')
            else:
                with open('ok_list.txt', 'a') as f:
                    f.write(f'{line.strip()}\n')
            print(line.strip())
