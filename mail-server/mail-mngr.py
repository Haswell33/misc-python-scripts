#!/usr/bin/env python3

import os
import argparse
import logging as log
import mysql.connector
from tabulate import tabulate
import pandas
from mysql.connector.errors import InterfaceError

USERS_COLUMN_NAME = 'users'
FORWARDINGS_COLUMN_NAME = 'forwardings'
DOMAINS_COLUMN_NAME = 'domains'

DEFAULTS = {  # need to install mysql-connector-python
    'DB_HOST': 'localhost',
    'DB_USER': 'mail-server_user',
    'DB_PORT': 3306,
    'DB_NAME': 'mail-server',
    'DB_PASSWORD_FILE': os.path.join(os.path.expanduser("~"), '.my.cnf'),
    'LIST_CHOICES': [USERS_COLUMN_NAME, FORWARDINGS_COLUMN_NAME, DOMAINS_COLUMN_NAME],
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
        pass

    def get_domains(self):
        pass

    def get_users(self, inactive, active, filter):
        query = "SELECT CONCAT(u.name, '@', d.name), CONCAT(CEILING(u.quota / 1024.0 / 1024), ' MB'), u.active FROM users u"
        if filter:
            query += f" JOIN domains d ON d.id = u.domain_id WHERE d.name LIKE '%{filter}%'"
        if inactive:
            query += f' {"WHERE" if "WHERE" not in query else "AND"} u.active = false'
        elif active:
            query += f' {"WHERE" if "WHERE" not in query else "AND"} u.active = true'
        result = self.database.select(query)
        print(len(result))
        MailManager.get_output(result, ['ID', 'E-mail', 'Quota', 'State'])

    def get_forwardings(self):
        pass

    @staticmethod
    def get_output(data, headers):
        for index, row in enumerate(data):  # append id on the beginning
            data[index] = tuple(str(index + 1)) + row
        print(tabulate(data, headers=headers))


class Database:

    def __init__(self, host, user, port, name, password):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            port=port,
            database=name,
            password=password)
        self.cursor = self.connection.cursor()

    def run_query(self, query):
        self.cursor.execute(query)
        log.debug(f'execute {query}')

    def insert(self, query):
        self.run_query(query)
        pass

    def update(self, query):
        self.run_query(query)
        pass

    def delete(self, query):
        self.run_query(query)
        pass

    def select(self, query):
        self.run_query(query)
        return database.cursor.fetchall()


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
                        help=f'Usable with -l/--list argument to filter output by domain',
                        type=str)
    parser.add_argument('--inactive',
                        help=f'Usable with -l/--list argument in order to get only inactive users in output',
                        action='store_true',
                        default=False)
    parser.add_argument('--active',
                        help=f'Usable with -l/--list argument in order to get only active users in output',
                        action='store_true',
                        default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        database = Database(args.dbHost, args.dbUser, args.dbPort, args.dbName, args.dbPasswd)
        mailManager = MailManager(database)
        mailManager.get_users(args.inactive, args.active, args.filter)
    except InterfaceError as e:  # cannot connect to mysql server
        log.error(f'{os.path.basename(__file__)}: {e}')
        print(f'{os.path.basename(__file__)}: {e}')
