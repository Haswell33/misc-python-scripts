import logging
import logging.config
import configparser
import time
import sys
import os
import smtplib
from dateutil.relativedelta import relativedelta
import ssl
import datetime
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import requests

# script desc:
# input params: py google-ads-invoice {receiver_email}

# Configuration
CONFIG = configparser.ConfigParser()  # loading a configparser lib


def get_invoice(receiver_email):
    '''
    response = client.get_service("InvoiceService").list_invoices(
        customer_id=customer_id,
        billing_setup=client.get_service("GoogleAdsService").billing_setup_path(
            customer_id, billing_setup_id
        ),
        # The year needs to be 2019 or later, per the docs:
        # https://developers.google.com/google-ads/api/docs/billing/invoice?hl=en#retrieving_invoices
        issue_year=str(last_month.year),
        issue_month=last_month.strftime("%B").upper(),
    )'''
    input_file = 'RUP_bestpractices.pdf'
    send_invoice_file_to_mail(input_file, receiver_email)


def send_invoice_file_to_mail(input_file, receiver_email):
    general = CONFIG['GENERAL']
    # message_template = CONFIG['MESSEGE']
    previous_month = datetime.now() + relativedelta(months=-1)
    message = MIMEMultipart()
    message['Subject'] = 'Google Ads invoice for ' + previous_month.strftime('%m') + '/' + str(time.strftime('%Y'))
    message['From'] = 'Malinka'
    message['To'] = receiver_email
    message_body = MIMEText('Google Ads invoice from ' + previous_month.strftime('%B') + ' has been attached to this mail', 'plain')
    message.attach(message_body)
    with open(input_file, 'rb') as file:
        attachment = MIMEApplication(file.read(), filename=os.path.basename(input_file))
    attachment['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(input_file)
    message.attach(attachment)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', general['port_ssl'], context=context) as smtp_server:
            smtp_server.login(general['sender_email'], general['sender_email_password'])
            smtp_server.sendmail(general['sender_email'], receiver_email, message.as_string())
            logging.info("message with invoice has been sent from '" + general['sender_email'] + "' to '" + receiver_email + "'")
    except smtplib.SMTPDataError as error_msg:
        logging.error(error_msg)
    except smtplib.SMTPAuthenticationError as error_msg:
        logging.error(error_msg)
    except smtplib.SMTPConnectError as error_msg:
        logging.error(error_msg)


def get_timestamp():
    # distract datetime on {day}-{month}-{year}, {hour}:{minutes}:{seconds}, if needs full datetime, just delete split
    curr_time = time.strftime('%d-%m-%Y_%H-%M-%S', time.localtime()).split('_', 1)
    return curr_time[0]  # curr_time[0] = {day}-{month}-{year}, curr_time[-1] = {hour}:{minutes}:{seconds}


def validate_and_start():  # execute a validator.py to check some things before start, if already check (checking by sys.argv[-1] = 'checked.py=executed') continue running script
    script_file = (sys.argv[0].split("\\"))[-1]
    list_of_params = []
    for param in range(0, len(sys.argv)):
        list_of_params.append(sys.argv[param])
    if sys.argv[-1] != 'validated':  # if input params does not have additional param with information about validator.py u need to check and perform a things below if
        try:
            os.system('py validator.py ' + str(get_params(list_of_params)))
        except IndexError:
            logging.error('Too few params were given on the input, sys.argv[1] = null; source: ' + script_file)
    else:  # everything checked, so script can start his work
        CONFIG.read(sys.argv[-2])
        filename = CONFIG['FILENAME']
        path = CONFIG['PATH']
        logging.config.fileConfig(path['config'] + filename[script_file.split('.')[0] + '_logging_config'])  # download the config file to logger
        if sys.argv[1] == 'help':
            get_help()
        else:
            get_invoice(sys.argv[1])


def get_help():
    print('\ndesc: script downloads google ADS invoice from google API, then sends it as a attachment in mail to specified receiver\n'
         'input: py ' + sys.argv[0] + ' {receiver-mail}\n')


def get_params(list_of_params):
    output_string = ''
    for count in range(0, len(list_of_params)):  # from 1, because sys.argv[0] is filename
        output_string += list_of_params[count] + ' '
    return output_string


if __name__ == '__main__':
    validate_and_start()