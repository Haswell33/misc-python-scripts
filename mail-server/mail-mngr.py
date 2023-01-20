#!/usr/bin/env python3

import os
import sys
import argparse
import logging as log
import mysql.connector
from tabulate import tabulate
from mysql.connector.errors import InterfaceError

USERS_COLUMN_NAME = 'users'
FORWARDINGS_COLUMN_NAME = 'forwardings'
DOMAINS_COLUMN_NAME = 'domains'

DEFAULTS = {  # need to install mysql-connector-python
    'DB_HOST': 'localhost',
    'DB_USER': 'mail-server_user',
    'DB_PORT': 3306,
    'DB_NAME': 'mail-server',
    'DB_PASSWORD_FILE': os.path.join(os.path.expanduser('~'), '.my.cnf'),
    'LIST_CHOICES': [USERS_COLUMN_NAME, FORWARDINGS_COLUMN_NAME, DOMAINS_COLUMN_NAME],
    'ADD_CHOICES': ['user', 'domain', 'forward'],
    # 'LOG_FILE': os.path.abspath(os.path.join(os.sep, 'var', 'log', f'{os.path.basename(__file__).split(".")[0]}.log')),
    'LOG_FILE': f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log',
}

log.basicConfig(filename=DEFAULTS['LOG_FILE'], format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log.DEBUG)


class MailManager:
    def __init__(self, database):
        self.database = database

    def create(self, selector):  # selector may be id or full name
        pass

    def delete(self, index):
        pass

    def update(self, index):
        pass

    def get_domains(self, inactive, active, filter_value):
        base_query = "SELECT d.id, d.name, d.active FROM domains d"
        result = self.database.select(MailManager.filter_query(base_query, active, inactive, filter_value))
        MailManager.get_output(result, ['ID', 'Name', 'State'])

    def get_users(self, inactive, active, filter_value):
        base_query = "SELECT u.id, CONCAT(u.name, '@', d.name), CONCAT(CEILING(u.quota / 1024.0 / 1024), ' MB'), u.active FROM users u JOIN domains d ON d.id = u.domain_id"
        result = self.database.select(MailManager.filter_query(base_query, active, inactive, filter_value))
        MailManager.get_output(result, ['ID', 'E-mail', 'Quota', 'State'])

    def get_forwardings(self, inactive, active, filter_value):
        base_query = "SELECT f.id, CONCAT(u.name, '@', d.name), f.destination, f.active FROM forwardings f JOIN users u ON u.ID = f.user_id JOIN domains d ON d.id = u.domain_id"
        result = self.database.select(MailManager.filter_query(base_query, active, inactive, filter_value))
        MailManager.get_output(result, ['ID', 'E-mail', 'Destination', 'State'])

    @staticmethod
    def get_output(data, headers):
        if len(data) == 0:
            raise LookupError(f'no results for query')
        # for index, row in enumerate(data):  # append id on the beginning
        #    data[index] = tuple(str(index + 1)) + row
        print(tabulate(data, headers=headers))

    @staticmethod
    def filter_query(query, active, inactive, filter_value):
        if filter_value:  # filtering by domain name
            query += f" WHERE d.name LIKE '%{filter_value}%'"
        if inactive:
            query += f' {"WHERE" if "WHERE" not in query else "AND"} u.active = false'
        elif active:
            query += f' {"WHERE" if "WHERE" not in query else "AND"} u.active = true'
        return query


class Database:
    def __init__(self, host, user, port, name, password, password_file):
        if not password and password_file and not os.path.isfile(password_file):
            raise OSError(f'Password file "{password_file}" does not exist, use -P/--password to input password as argument or create this file, see details how to create this file in MySQL docs')
        #test = host=host, user=user, port=port, database=name)
        config = {'host': host, 'user': user, 'port': port, 'database': name}
        if password:
            config['password'] = password
        elif password_file:
            config['read_default_file'] = password_file
        self.connection = mysql.connector.connect(**config)
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


def is_writing():
    if '-a' in sys.argv or '--add' in sys.argv or '-u' in sys.argv or '--update' in sys.argv or '-d' or '--delete':  # if adding, updating or deleting some data in db
        return True
    else:
        return False


def valid_value_type(value):
    print(value)
    if '-a' in sys.argv or '--add' in sys.argv:
        try:
            str(value)
        except ValueError:
            raise argparse.ArgumentTypeError('invalid type. Expected type is string')
    elif '-u' in sys.argv or '--update' in sys.argv or '-d' or '--delete':
        try:
            int(value)
        except ValueError:
            raise argparse.ArgumentTypeError('invalid type, it should be index of database. Expected type is integer')
    return value


def parse_args():
    writing = is_writing()
    parser = argparse.ArgumentParser(description='Script to manage database of mail server')
    parser.add_argument('-H', '--dbHost',
                        help=f'Database host, default is {DEFAULTS["DB_HOST"]}',
                        type=str,
                        metavar='host',
                        default=DEFAULTS['DB_HOST'])
    parser.add_argument('-U', '--dbUser',
                        help=f'Database user, default is {DEFAULTS["DB_USER"]}',
                        type=str,
                        metavar='user',
                        default=DEFAULTS['DB_USER'])
    parser.add_argument('-p', '--dbPort',
                        help=f'Database port, default is {DEFAULTS["DB_PORT"]}',
                        type=int,
                        metavar='port',
                        default=DEFAULTS['DB_PORT'])
    parser.add_argument('-D', '--dbName',
                        help=f'Database name, default is {DEFAULTS["DB_NAME"]}',
                        type=str,
                        metavar='database',
                        default=DEFAULTS['DB_NAME'])
    parser.add_argument('-P', '--dbPasswd',
                        help='Database password, choose this option if you do not want get password from file',
                        type=str,
                        metavar='password')
    parser.add_argument('--passwdFile',
                        help=f'File with password to database, default is {DEFAULTS["DB_PASSWORD_FILE"]}',
                        type=str,
                        metavar='file',
                        default=DEFAULTS["DB_PASSWORD_FILE"])
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
    parser.add_argument('-a', '--add',
                        help='Type to ',
                        type=str,
                        choices=DEFAULTS['ADD_CHOICES'])
    parser.add_argument('-u', '--update',
                        help='Index which you want to update',
                        type=str,
                        choices=DEFAULTS['ADD_CHOICES'])
    parser.add_argument('-d', '--delete',
                        help='Index which you want to delete',
                        type=str,
                        choices=DEFAULTS['ADD_CHOICES'])
    parser.add_argument('-v', '--value',
                        help=f'Usable with -a/--add argument to specify value of adding data',
                        type=valid_value_type,
                        required=writing)
    args = parser.parse_args()
    # if args.list and writing:
    #    raise parser.error('usage of -l/--list argument is invalid while writing data by using -a/--add, -u/--update or -d/--delete argument')
    # elif args.filter and writing:
    #     raise parser.error('usage of -f/--filter argument is invalid while writing data by using -a/--add, -u/--update or -d/--delete argument')
    return args


if __name__ == "__main__":
    args = parse_args()
    try:
        mailManager = MailManager(Database(args.dbHost, args.dbUser, args.dbPort, args.dbName, args.dbPasswd, args.passwdFile))
        if args.add:yght
            mailManager.create(args.value)
        elif args.update:
            mailManager.update(args.value)
        elif args.delete:
            mailManager.delete(args.value)

        if args.list == USERS_COLUMN_NAME:
            mailManager.get_users(args.inactive, args.active, args.filter)
        elif args.list == FORWARDINGS_COLUMN_NAME:
            mailManager.get_forwardings(args.inactive, args.active, args.filter)
        elif args.list == DOMAINS_COLUMN_NAME:
            mailManager.get_domains(args.inactive, args.active, args.filter)
    except (OSError, argparse.ArgumentError, InterfaceError) as e:  # cannot connect to mysql server
        log.error(f'{os.path.basename(__file__)}: {e}')
        print(f'{os.path.basename(__file__)}: {e}')
    except LookupError as e:
        print(e)
