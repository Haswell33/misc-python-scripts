#!/usr/bin/env python3

import os
import re

REGEX = """[\s]*Logger.getLogger\(['"]{1}([a-zA-Z\.]*)['"]\)"""
def get_loggers(path):
    loggers = ""
    with os.scandir(path) as directory:
        for entry in directory:
            if entry.is_file():
                with open(entry.path) as f_r:
                    lines = f_r.readlines()
                    for line in lines:
                        result = re.search(REGEX, line)
                        if result:
                            loggers += f'log4j.logger.{result.group(1)}=INFO\n'
            elif entry.is_dir():
                loggers += get_loggers(entry.path)
    return loggers



if __name__ == "__main__":
    print(get_loggers('/mnt/d/Programs/Repository/Groovy/atlassian/jira/src/main/resources/lib/redge'))
