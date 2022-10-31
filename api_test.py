# Name:              api_test.py
# Developers:        Kevin Alexander Martinez Sanchez
# Creation date:     30th September of 2022
# Modification date: 30th September of 2022

import json
import flask
import requests
import traceback
import pandas as pd
from helpers.constants import API_URL, TABLE, dynamodb_client
from flask import *
import time

app = Flask(__name__)

def get_pages_dynamo_data_batches(date_=None):

    try:
        paginator = dynamodb_client.get_paginator('scan')
        operation_parameters = {
            'TableName': TABLE
        }

        page_iterator = paginator.paginate(**operation_parameters)
        pages = []

        for page in page_iterator:
            pages.append(page)

        return pages
    except Exception as e:
        return f"{e}\n\n{traceback.format_exc()}"


def convert_dynamo_data_to_df(scan):

    if scan is None:
        return None

    columns = list(scan['Items'][0].keys())
    df_dynamo = pd.DataFrame(columns=columns)

    for item in scan['Items']:
        dict_ = {}
        for key_ in item.keys():
            temp = item[key_]
            for key_type in temp:
                dict_[key_] = temp[key_type]
        df_dynamo.loc[df_dynamo.shape[0]] = dict_

    return df_dynamo


def get_all_dynamo_db_data(date_=None):
    try:
        pages = get_pages_dynamo_data_batches(date_)
        all_data_dfs = [
            convert_dynamo_data_to_df(page) for page in pages
        ]

        df_dynamo = pd.concat(all_data_dfs).reset_index(drop=True)

        return df_dynamo
    except Exception as e:
        return f"{e}\n\n{traceback.format_exc()}"
    

def get_data():
    try:
        data = requests.get(API_URL).json()
        return data
    except Exception as e:
        return f'error: {e}'


def data_to_df(data:dict):
    try:
        df = pd.DataFrame(data['results'])
        return df
    except Exception as e:
        error = 'data incorrecta'
        return f'error: {error}, {e}'
    
    
def get_request(request:dict):
#def get_request():
    logger.info(f"Request: {request}")
    method = request.method
    if method != "GET":
        return 'invalid method'
    
    content_type = request.headers.get("content-type")
    if content_type != "application/json":
        return 'invalid content_type'

    body_request = request.get_json()

    if body_request is None:
        return 'body_request is None'
    if list(body_request['data'].keys()) != EXPECTED_KEYS:
        print(f'validador keys data: {body_request["data"].keys()}')
        print(EXPECTED_KEYS)
        return 'Invalid keys'
    
    event = json.loads(request.data.decode("utf-8"))
    initial_data = event.get("data")
              
    if isinstance(initial_data, dict):
        customer_id = initial_data.get("customer_id", "unknown")
    
    try:
        obtain_data = get_data()
        df = data_to_df(obtain_data)
        df_dynamo = get_all_dynamo_db_data()
        df_concat = pd.concat([df, df_dynamo], axis=1, join="inner")
        df_search = df_concat[df_concat['customer_id'] == '1123']
        value_cash = str(df_search.cash_amount.to_list()).replace('[', '').replace(']', '')
        value_customer_id = str(df_search.customer_id.to_list()).replace('[', '').replace(']', '')
        value_date = str(df_search.ex_dividend_date.to_list()).replace('[', '').replace(']', '')
        value_money = str(df_search.currency.to_list()).replace('[', '').replace(']', '')

        builtins.customer_id = customer_id
        request_data = {"data": {"customer_id": value_customer_id,
                                 "value_cash": value_cash,
                                 "value_date": value_date,
                                 "value_money": value_money
                                 }
                        }
        return request_data
    except Exception as e:
        print(e)

              
def pd_read_s3_csv(key, sep=','):
    """ Read single csv file from S3 """

    obj = s3_client.get_object(Bucket=BUCKET, Key=key)
    df = pd.read_csv(
        BytesIO(obj['Body'].read()),
        sep=sep
    )
    return df


def send_df_to_s3(df, key):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_resource.Object(BUCKET, key).put(Body=csv_buffer.getvalue())
              

def df_to_local(df, path:str):
    path_document = path + 'document_validation.csv'
    df.to_csv(path_document, sep=',', encoding='utf-8', index=False)
    return f'write document in {path_document}'


@app.route("/")
def hello():
    print("exitoso caso 1")
    return "Hello World!"


@app.route("/main", methods=['GET'])
def main(request:dict):
#def main():
    try:
        print("exitoso")
        request = get_request()
        #print(request)
        print("status: 200")
        return str(request)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port="4040")
