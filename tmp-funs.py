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
        host='test',
        user='test.test',
        password='test',
        database='testdb')
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
    testvar1 = ".selectize-control.plugin-drag_drop.multi>.selectize-input>div.ui-sortable-placeholder{visibility:visible!important;background:#f2f2f2!important;background:rgba(0,0,0,.06)!important;border:0 none!important;-webkit-box-shadow:inset 0 0 12px 4px #fff;box-shadow:inset 0 0 12px 4px #fff}.selectize-control.plugin-drag_drop .ui-sortable-placeholder::after{content:'!';visibility:hidden}.selectize-control.plugin-drag_drop .ui-sortable-helper{-webkit-box-shadow:0 2px 5px rgba(0,0,0,.2);box-shadow:0 2px 5px rgba(0,0,0,.2)}.selectize-dropdown-header{position:relative;padding:3px 12px;border-bottom:1px solid #d0d0d0;background:#f8f8f8;-webkit-border-radius:4px 4px 0 0;-moz-border-radius:4px 4px 0 0;border-radius:4px 4px 0 0}.selectize-dropdown-header-close{position:absolute;right:12px;top:50%;color:#333;opacity:.4;margin-top:-12px;line-height:20px;font-size:20px!important}.selectize-dropdown-header-close:hover{color:#000}.selectize-dropdown.plugin-optgroup_columns .optgroup{border-right:1px solid #f2f2f2;border-top:0 none;float:left;-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}.selectize-dropdown.plugin-optgroup_columns .optgroup:last-child{border-right:0 none}.selectize-dropdown.plugin-optgroup_columns .optgroup:before{display:none}.selectize-dropdown.plugin-optgroup_columns .optgroup-header{border-top:0 none}.selectize-control.plugin-remove_button [data-value]{position:relative;padding-right:24px!important}.selectize-control.plugin-remove_button [data-value] .remove{z-index:1;position:absolute;top:0;right:0;bottom:0;width:17px;text-align:center;font-weight:700;font-size:12px;color:inherit;text-decoration:none;vertical-align:middle;display:inline-block;padding:1px 0 0 0;border-left:1px solid transparent;-webkit-border-radius:0 2px 2px 0;-moz-border-radius:0 2px 2px 0;border-radius:0 2px 2px 0;-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}.selectize-control.plugin-remove_button [data-value] .remove:hover{background:rgba(0,0,0,.05)}.selectize-control.plugin-remove_button [data-value].active .remove{border-left-color:transparent}.selectize-control.plugin-remove_button .disabled [data-value] .remove:hover{background:0 0}.selectize-control.plugin-remove_button .disabled [data-value] .remove{border-left-color:rgba(77,77,77,0)}.selectize-control.plugin-remove_button .remove-single{position:absolute;right:0;top:0;font-size:23px}.selectize-control{position:relative}.selectize-dropdown,.selectize-input,.selectize-input input{color:#333;font-family:inherit;font-size:inherit;line-height:20px;-webkit-font-smoothing:inherit}.selectize-control.single .selectize-input.input-active,.selectize-input{background:#fff;cursor:text;display:inline-block}.selectize-input{border:1px solid #ccc;padding:6px 12px;display:inline-block;width:100%;overflow:hidden;position:relative;z-index:1;-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;-webkit-box-shadow:none;box-shadow:none;-webkit-border-radius:4px;-moz-border-radius:4px;border-radius:4px}.selectize-control.multi .selectize-input.has-items{padding:5px 12px 2px}.selectize-input.full{background-color:#fff}.selectize-input.disabled,.selectize-input.disabled *{cursor:default!important}.selectize-input.focus{-webkit-box-shadow:inset 0 1px 2px rgba(0,0,0,.15);box-shadow:inset 0 1px 2px rgba(0,0,0,.15)}.selectize-input.dropdown-active{-webkit-border-radius:4px 4px 0 0;-moz-border-radius:4px 4px 0 0;border-radius:4px 4px 0 0}.selectize-input>*{vertical-align:baseline;display:-moz-inline-stack;display:inline-block;zoom:1}.selectize-control.multi .selectize-input>div{cursor:pointer;margin:0 3px 3px 0;padding:1px 3px;background:#efefef;color:#333;border:0 solid transparent}.selectize-control.multi .selectize-input>div.active{background:#428bca;color:#fff;border:0 solid transparent}.selectize-control.multi .selectize-input.disabled>div,.selectize-control.multi .selectize-input.disabled>div.active{color:grey;background:#fff;border:0 solid rgba(77,77,77,0)}.selectize-input>input{display:inline-block!important;padding:0!important;min-height:0!important;max-height:none!important;max-width:100%!important;margin:0!important;text-indent:0!important;border:0 none!important;background:0 0!important;line-height:inherit!important;-webkit-user-select:auto!important;-webkit-box-shadow:none!important;box-shadow:none!important}.selectize-input>input::-ms-clear{display:none}.selectize-input>input:focus{outline:0!important}.selectize-input::after{content:' ';display:block;clear:left}.selectize-input.dropdown-active::before{content:' ';display:block;position:absolute;background:#fff;height:1px;bottom:0;left:0;right:0}.selectize-dropdown{position:absolute;z-index:10;border:1px solid #d0d0d0;background:#fff;margin:-1px 0 0 0;border-top:0 none;-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;-webkit-box-shadow:0 1px 3px rgba(0,0,0,.1);box-shadow:0 1px 3px rgba(0,0,0,.1);-webkit-border-radius:0 0 4px 4px;-moz-border-radius:0 0 4px 4px;border-radius:0 0 4px 4px}.selectize-dropdown [data-selectable]{cursor:pointer;overflow:hidden}.selectize-dropdown [data-selectable] .highlight{background:rgba(255,237,40,.4);-webkit-border-radius:1px;-moz-border-radius:1px;border-radius:1px}.selectize-dropdown .optgroup-header,.selectize-dropdown .option{padding:3px 12px}.selectize-dropdown .option,.selectize-dropdown [data-disabled],.selectize-dropdown [data-disabled] [data-selectable].option{cursor:inherit;opacity:.5}.selectize-dropdown [data-selectable].option{opacity:1}.selectize-dropdown .optgroup:first-child .optgroup-header{border-top:0 none}.selectize-dropdown .optgroup-header{color:#777;background:#fff;cursor:default}.selectize-dropdown .active{background-color:#f5f5f5;color:#262626}.selectize-dropdown .active.create{color:#262626}.selectize-dropdown .create{color:rgba(51,51,51,.5)}.selectize-dropdown-content{overflow-y:auto;overflow-x:hidden;max-height:200px;-webkit-overflow-scrolling:touch}.selectize-control.single .selectize-input,.selectize-control.single .selectize-input input{cursor:pointer}.selectize-control.single .selectize-input.input-active,.selectize-control.single .selectize-input.input-active input{cursor:text}.selectize-control.single .selectize-input:after{content:' ';display:block;position:absolute;top:50%;right:17px;margin-top:-3px;width:0;height:0;border-style:solid;border-width:5px 5px 0 5px;border-color:#333 transparent transparent transparent}.selectize-control.single .selectize-input.dropdown-active:after{margin-top:-4px;border-width:0 5px 5px 5px;border-color:transparent transparent #333 transparent}.selectize-control.rtl.single .selectize-input:after{left:17px;right:auto}.selectize-control.rtl .selectize-input>input{margin:0 4px 0 -2px!important}.selectize-control .selectize-input.disabled{opacity:.5;background-color:#fff}.selectize-dropdown,.selectize-dropdown.form-control{height:auto;padding:0;margin:2px 0 0 0;z-index:1000;background:#fff;border:1px solid #ccc;border:1px solid rgba(0,0,0,.15);-webkit-border-radius:4px;-moz-border-radius:4px;border-radius:4px;-webkit-box-shadow:0 6px 12px rgba(0,0,0,.175);box-shadow:0 6px 12px rgba(0,0,0,.175)}.selectize-dropdown .optgroup-header{font-size:12px;line-height:1.42857143}.selectize-dropdown .optgroup:first-child:before{display:none}.selectize-dropdown .optgroup:before{content:' ';display:block;height:1px;margin:9px 0;overflow:hidden;background-color:#e5e5e5;margin-left:-12px;margin-right:-12px}.selectize-dropdown-content{padding:5px 0}.selectize-dropdown-header{padding:6px 12px}.selectize-input{min-height:34px}.selectize-input.dropdown-active{-webkit-border-radius:4px;-moz-border-radius:4px;border-radius:4px}.selectize-input.dropdown-active::before{display:none}.selectize-input.focus{border-color:#66afe9;outline:0;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgba(102,175,233,.6);box-shadow:inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgba(102,175,233,.6)}.has-error .selectize-input{border-color:#a94442;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,.075);box-shadow:inset 0 1px 1px rgba(0,0,0,.075)}.has-error .selectize-input:focus{border-color:#843534;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,.075),0 0 6px #ce8483;box-shadow:inset 0 1px 1px rgba(0,0,0,.075),0 0 6px #ce8483}.selectize-control.multi .selectize-input.has-items{padding-left:9px;padding-right:9px}.selectize-control.multi .selectize-input>div{-webkit-border-radius:3px;-moz-border-radius:3px;border-radius:3px}.form-control.selectize-control{padding:0;height:auto;border:none;background:0 0;-webkit-box-shadow:none;box-shadow:none;-webkit-border-radius:0;-moz-border-radius:0;border-radius:0}"
    with open('test.txt', 'w') as file:
        testvar2 = testvar1.replace(';', ';\n')
        testvar3 = testvar2.replace("}.", "\n}\n.")
        file.writelines(testvar3)

    #read_file_to_class()
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
