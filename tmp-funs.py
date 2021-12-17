import os
import re
import mysql.connector
import csv
import argparse
import struct
import sys
import pathlib


class StoragePeakSample:
    workspace = ''
    used = 0
    date = 0

    def __init__(self, workspace, used, date):
        self.workspace = workspace
        self.used = used / 1000000000
        self.date = date

class Customers:
    pivot_name = ''
    internal_workspace = ''
    external_workspace = ''

    def __init__(self, pivot_name, internal_workspace, external_workspace):
        self.pivot_name = pivot_name
        self.internal_workspace = internal_workspace
        self.external_workspace = external_workspace

class StoragePeak:
    used = 0
    date = 0

    def __init__(self, used, date):
        self.used = used
        self.date = date.strftime('%Y-%m')

class Lines:
    line = ''

    def __init__(self, line):
        self.line = line


def read_file_to_class():
    test_list = []
    path = 'test2.txt'
    with open(path, 'rb') as input_file:
        for line in input_file:
            currentPlace = line[:-1]
            test_list.append(Lines(currentPlace))
    with open('output.txt', 'w') as output_file:
        for elem in test_list:
            x = str(elem).split(',')
            for i in x:
                output_file.write(i + '\t')
            output_file.write('\n\n')


def decode_binary_file(position):
    file = open('get_billing_data.do')
    response = file.read().replace("\n", " ")
    file.close()
    billing_record_size = struct.unpack('qqii', response[:24])[2] / 8
    unpack_format = f'qqii{str(billing_record_size).split(".")[0]}dqddd'
    unpack_response = struct.unpack(unpack_format, response)
    billing_data = unpack_response[position:len(unpack_response) - 4]  # positions: 1=new, 2=received, 3=used, 4=sent
    for billing_sample in billing_data[4:len(billing_data):5]:
        #billing_list.append(billing_sample)
        print(billing_sample)


def add_path_string():
    tmp_list = []
    with open('ncplus-workspaces.txt', 'r') as output_file:
        for line in output_file:
            currentPlace = line[:-1]
            tmp_list.append(currentPlace)
    print(tmp_list)
    with open('test.txt', 'w') as output_file:
        for item in tmp_list:
            output_file.write('<path>' + item + '</path>\n')
    for i in tmp_list:
        print(i)


def count_dirs():
    total_dir = 0
    for base, dirs, files in os.walk('tmp/raporty_old'):
        print('Searching in : ', base)
        for directories in dirs:
            total_dir += 1
    print(total_dir)


def exec_test(file):
    exec(file)


def clear_logs():
    with open('config/empty_workspaces_old.txt', 'r') as log_file:
        #logs = log_file.read()
        lines = log_file.readlines()
        with open('logs/parsed_bulk-billing.log', 'w') as parsed_log_file:
            for line in lines:
                tmp = re.search(r'Report for (.*?) not created\n', line).group(1)
                parsed_log_file.writelines(tmp + '\n')


def dodaj_kropke_na_poczatku():
    with open('tmp/dodaj_kropke_na_poczatku.txt', 'r') as first_file:
        lines = first_file.readlines()
        with open('dodalem_kropke_na_poczatku.txt', 'w') as second_file:
            for line in lines:
                second_file.write('.' + line.strip() + '\n')


class ConvertToString(mysql.connector.conversion.MySQLConverter):
    def row_to_python(self, row, fields):
        row = super(ConvertToString, self).row_to_python(row, fields)

        def to_unicode(column):
            if isinstance(column, bytearray):
                return column.decode('utf-8')
            return column
        return[to_unicode(column) for column in row]


def test_sql():
    storage_peak_samples_list = []
    storage_peak_list = []
    datetime_list = []
    workspaces_list = ['tvnplayer', 'tvn24go', 'tvnplayerncp', 'tvn', 'TVN-Adserver', 'TVN-Xnews']
    begin_date = '2021-06-01'
    end_date = '2021-07-01'
    o2billing_db = mysql.connector.connect(
        converter_class=ConvertToString,
        host='hops.hops.hops.hops',
        user='hops.hops',
        password='hops',
        database='hopsdb')
    cursor = o2billing_db.cursor(buffered=True)
    for workspace in workspaces_list:
        cursor.execute("""
                       SELECT date, used FROM records
                       WHERE workspace_id = (SELECT id from workspaces WHERE name = ('%s'))
                       AND date > ('%s') AND date < ('%s')
                       ORDER BY used DESC LIMIT 1
                       """%(workspace, begin_date, end_date))
        for row in cursor.fetchall():
            datetime_list.append(row[0])
    for datetime_sample in datetime_list:
        used_sum = 0
        for workspace in workspaces_list:
            cursor.execute("""
                           SELECT ('%s'), used, date  FROM records
                           WHERE workspace_id = (SELECT id from workspaces WHERE name = ('%s'))
                           AND date = ('%s')
                           """%(workspace, workspace, datetime_sample))
            for row in cursor.fetchall():
                # print('\t' + workspace + ' \t\t' + str(row[1] / 1000000000) + ' \t\t' + str(row[2]))
                used_sum += row[1]
        # print('\n')
        storage_peak_samples_list.append(StoragePeakSample('', used_sum, datetime_sample))
    # for i in storage_peak_list:
    #    print(str(i.date) + ' ' + str(i.used))
    for i in storage_peak_samples_list:
        max_used = max(StoragePeakSample.used for StoragePeakSample in storage_peak_samples_list)
        if i.used == max_used:
            storage_peak_list.append(StoragePeak(max_used, i.date))
            print('time: ' + str(i.date))
    for i in storage_peak_list:
        print(str(i.used) + ' ' + str(i.date))


def create_xml_from_csv_workspaces_list():
    exception_list = []
    customers = []
    with open('config/workspaces_list.csv', 'r') as input_csv_file:
        reader = csv.reader(input_csv_file, delimiter=';')
        for row in reader:
            if row[0] != '':
                customers.append(Customers(row[0], row[1], row[2]))
    del customers[0]  # delete title row
    for i in customers:
        print(i.pivot_name + '\n\t' + i.internal_workspace + '\n\t' + i.external_workspace)
    for i in customers:
        workspaces_list = i.internal_workspace
        for workspace in str(workspaces_list).split(', '):
                exception_list.append(workspace)
    for i in exception_list:
        print(i)


def create_dir(path):
    with open(path, 'a') as file:
        pass


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-b', '--beginDate', help='Date in format {-b yyyy-mm-dd}. It is not required, default value is first day of previous month', type=str, default=_get_first_day_of_prev_month())
    arg_parser.add_argument('-e', '--endDate', help='Date in format {-e yyyy-mm-dd}. It is not required, default value is last day of previous month', type=str, default=_get_first_day_of_curr_month())
    arg_parser.add_argument('-pk', '--projectKey', help='Filter by project key in format {-pk projectKey}. It is not required, in this case script will generate billed hours for all project keys', type=str, default='')
    arg_parser.add_argument('-fh', '--ftpHost', help='Dest FTP host in format {-fh host}. It is not required', type=str, default=False)
    arg_parser.add_argument('-fd', '--ftpDir', help='Dest FTP dir in format {-fd path/to/dir}. It is not required', type=str)
    arg_parser.add_argument('-fu', '--ftpUser', help='FTP username in format {-fu username}. It is not required', type=str)
    arg_parser.add_argument('-fp', '--ftpPassword', help='FTP password in format {-fp password}. It is not required', type=str)
    arg_parser.add_argument('-m', '--recipientMail', nargs='+', help='Mail of recipient in format {-m email@} or {-m email1, email2}. It is not required', type=str, default=False)
    return arg_parser.parse_args()


if __name__ == "__main__":
    read_file_to_class()
    #add_path_string()
    #count_dirs()
    #clear_logs()
    #dodaj_kropke_na_poczatku()
    #exec_test('billing.py -b 2021-10-15 -e 2021-10-16 -w fina')
    # create_xml_from_csv_workspaces_list()
    # create_dir('1/2/3/dupa.csv')
    # decode_binary_file(4)
    #test = 'test/test/test/test/Kontraktorzy'
    #print(test.rsplit('/', 1)[0])
