import requests
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = os.getenv('PROJECT_ID')
TOKEN = os.getenv('TOKEN_S3')
bucket_name = os.getenv('BUCKET_NAME')
tenant_name = os.getenv('TENANT_NAME')


def get_user_s3():
    url = f"https://api.clo.ru/v2/projects/{PROJECT_ID}/s3/users"

    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

    r = requests.get(url, headers=header)

    if r.status_code != 200:
        return r.text

    parse = r.json()

    return parse['result'][0]['id']


def credentials_request():
    object_id = get_user_s3()

    url = f"https://api.clo.ru/v2/s3/users/{object_id}/credentials"

    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TOKEN}'}

    r = requests.get(url=url, headers=header)

    access_key, secret_key = r.json()['result'][0]['access_key'], r.json()['result'][0]['secret_key']

    return access_key, secret_key

