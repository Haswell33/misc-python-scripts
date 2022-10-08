import requests
import argparse

BASE_URL = 'https://login.microsoftonline.com'


def get_token(client_id, client_secret, scope, grant_type, tenant_id):
    session = requests.session()
    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': grant_type,
        'scope': scope
    }
    url = f'{BASE_URL}/{tenant_id}/oauth2/v2.0/token'
    print(url)
    response = session.post(
        url,
        data=body,
        headers={
            'Content-Type': "application/x-www-form-urlencoded"
        }
    )
    if response.ok:
        return response.json()['access_token']
    else:
        return response.reason + str(response.status_code) + ': ' + str(response.request) + str(response.text)


def parse_args():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--clientId', help='', type=str, required=True)
    arg_parser.add_argument('--clientSecret', help='', type=str, required=True)
    arg_parser.add_argument('--grantType', help='', type=str, required=True)
    arg_parser.add_argument('--scope', help='', type=str, required=True)
    arg_parser.add_argument('--tenantId', help='', type=str, required=True)
    return arg_parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    token = get_token(args.clientId, args.clientSecret, args.scope, args.grantType, args.tenantId)
    print(token)
