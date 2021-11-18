#!/usr/bin/env python3

import hashlib
import sys


def checksum_md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == '__main__':
    filename = sys.argv[1].split('/')[-1]
    with open('checksum-' + filename + '.md5', 'w') as md5_file:
        md5_file.write(str(filename) + ' ' + 'checksum: ' + str(checksum_md5(sys.argv[1])))
        print('checksum has been stored in ' + 'checksum-' + filename + '.md5')
