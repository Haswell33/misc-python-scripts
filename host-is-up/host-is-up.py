import os
import logging
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

logging.basicConfig(filename=f'{os.path.abspath(os.path.dirname(__file__))}/logs/{os.path.basename(__file__).split(".")[0]}.log', format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)


def host_is_up(ip_address, timeout):
    start_timestamp = _get_datetime_object(datetime.now().strftime('%H:%M:%S'))
    end_timestamp = start_timestamp + relativedelta(seconds=+timeout)  # setting up timeout
    waiting = True
    while waiting:
        response = os.popen(f'ping -n 1 {ip_address}').read()  # for linux -c, for windows -n
        if 'Destination host unreachable' in response or 'Request timed out' in response or 'Received = 0' in response:
            time.sleep(1)
            print(f'waiting for host...')
            if datetime.now().strftime("%H:%M:%S") >= end_timestamp.strftime("%H:%M:%S"):
                print(f'{os.path.basename(__file__)}: an error has occurred, check logs for more information')
                logging.error(f'Request timed out, {ip_address} did not response to ping in {int((end_timestamp - start_timestamp).total_seconds())} seconds')
                return False
        else:
            print(f'{ip_address} is up')
            logging.info(f'{ip_address} is up')
            waiting = False
    return True


def _get_datetime_object(date):
    return datetime.strptime(date, '%H:%M:%S')


if __name__ == "__main__":
    host_is_up('192.172.0.1', 30)  # ip address, timeout in seconds
