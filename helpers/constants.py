# Name:              constants.py
# Developers:        Kevin Alexander Martinez Sanchez
# Creation date:     29th September of 2022
# Modification date: 29th September of 2022

import os
import boto3

API = '' # YOUR API
API_URL = f'https://api.polygon.io/v3/reference/dividends?apiKey={API}'

EXPECTED_KEYS = ['']

TABLE = '' # Change table for one that they have available in their Amazon account

REGION_NAME = '' # your region name in amazon
PROFILE_NAME = '' # your profile name in amazon

boto3.setup_default_session(profile_name=PROFILE_NAME)
os.environ['ENVIRONMENT'] = 'production'

s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')
dynamodb_client = boto3.client("dynamodb")
