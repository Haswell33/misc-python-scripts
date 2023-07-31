if __name__ == '__main__':
    with open('output.txt', 'w') as f_w:
        f_w.write('')
    with open('hosts.txt', 'r') as f_r:
        for line in f_r.readlines():
            line_split = line.replace('\n', '').split(':')
            host_name = line_split[0]
            host_address = line_split[1]
            with open('output.txt', 'a') as f_w:
                f_w.write(f'{host_name} ansible_host={host_address} ansible_connection=ssh\n')
