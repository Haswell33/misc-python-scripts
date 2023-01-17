#!/usr/bin/env python3

import os
import argparse
import logging as log
import mysql.connector
from mysql.connector.errors import InterfaceError

USER_LIST = 'users'
FORWARDINGS_LIST = 'forwardings'
DOMAINS_LIST = 'domains'

DEFAULTS = {  # need to install mysql-connector-python
    'DB_HOST': 'localhost',
    'DB_USER': 'mail-server_user',
    'DB_PORT': 3306,
    'DB_NAME': 'mail-server',
    'DB_PASSWORD_FILE': os.path.join(os.path.expanduser("~"), '.my.cnf'),
    'LIST_CHOICES': [USER_LIST, FORWARDINGS_LIST, DOMAINS_LIST],
    # 'LOG_FILE': os.path.abspath(os.path.join(os.sep, 'var', 'log', f'{os.path.basename(__file__).split(".")[0]}.log')),
    'LOG_FILE': f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log',
}

log.basicConfig(filename=DEFAULTS['LOG_FILE'], format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log.DEBUG)


class MailManager:
    def __init__(self, database):
        self.database = database

    def create_user(self, selector, password):  # selector may be id or full name
        pass

    def delete_user(self, selector):
        pass

    def update_user(self, selector):
        print(test)
        pass

    def get_domains(self):
        pass

    def get_users(self, inactive, filter):
        cmd = 'SELECT * FROM users u'
        if filter:
            cmd += f" JOIN domains d ON d.id = u.domain_id WHERE d.name LIKE '%{filter}%'"
        if inactive:
            cmd += f' {"WHERE" if "WHERE" not in cmd else "AND"} u.active = true'
        print(cmd)
        #database.cursor.execute(cmd)

        result = database.cursor.fetchall()
        for x in result:
            print(x)

    def get_forwardings(self):
        pass


class Database:

    def __init__(self, host, user, port, name, password):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            port=port,
            database=name,
            password=password
        )
        self.cursor = self.connection.cursor()

    def insert(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def select(self):
        pass


def parse_args():
    parser = argparse.ArgumentParser(description='Script to manage database of mail server')
    parser.add_argument('-H', '--dbHost',
                        help=f'Database host, default is {DEFAULTS["DB_HOST"]}',
                        type=str,
                        metavar='host',
                        default=DEFAULTS['DB_HOST'])
    parser.add_argument('-u', '--dbUser',
                        help=f'Database user, default is {DEFAULTS["DB_USER"]}',
                        type=str,
                        metavar='user',
                        default=DEFAULTS['DB_USER'])
    parser.add_argument('-p', '--dbPort',
                        help=f'Database port, default is {DEFAULTS["DB_PORT"]}',
                        type=int,
                        metavar='port',
                        default=DEFAULTS['DB_PORT'])
    parser.add_argument('-d', '--dbName',
                        help=f'Database name, default is {DEFAULTS["DB_NAME"]}',
                        type=str,
                        metavar='database',
                        default=DEFAULTS['DB_NAME'])
    parser.add_argument('-P', '--dbPasswd',
                        help='Database password',
                        type=str,
                        metavar='password')
    parser.add_argument('--dbPasswdFile',
                        help=f'File with password to database, default is {DEFAULTS["DB_PASSWORD_FILE"]}',
                        type=str,
                        metavar='password')
    parser.add_argument('-l', '--list',
                        help=f'List users, forwarding or domains',
                        type=str,
                        choices=DEFAULTS['LIST_CHOICES'])
    parser.add_argument('-f', '--filter',
                        help=f'Usable with -l/--list argument to filter output',
                        type=str)
    parser.add_argument('--inactive',
                        help=f'Usable with -l/--list argument in order to include also inactive users in output',
                        action='store_true',
                        default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        database = Database(args.dbHost, args.dbUser, args.dbPort, args.dbName, args.dbPasswd)
        mailManager = MailManager(database)
        mailManager.get_users(args.inactive, args.filter)
    except InterfaceError as e:  # cannot connect to mysql server
        log.error(f'{os.path.basename(__file__)}: {e}')
        print(f'{os.path.basename(__file__)}: {e}')
