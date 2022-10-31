# Name:              api_test.py
# Developers:        Kevin Alexander Martinez Sanchez
# Creation date:     30th September of 2022
# Modification date: 31th September of 2022
# Diagram link:      https://lucid.app/lucidchart/20424413-1db2-43f5-80e2-0c32365da439/edit?viewport_loc=44%2C-12%2C1579%2C776%2C0_0&invitationId=inv_b9af206f-1e47-4e1c-b953-c44427f45df8

import json
import flask
import requests
import builtins
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
    
    
def get_request(request):
    str_to_dict = '{' + request + '}'
    json_request = json.dumps(str_to_dict)
    str_to_dict = json_request.replace("\'", "\"")
    print(str_to_dict)
    request_ = json.loads(str_to_dict)
    res = json.loads(request_)
    print(f"Request: {res}")
    customer_id = res.get("customer_id")
    
    try:
        obtain_data = get_data()
        df = data_to_df(obtain_data)
        df_dynamo = get_all_dynamo_db_data()
        df_concat = pd.concat([df, df_dynamo], axis=1, join="inner")
        df_search = df_concat[df_concat['customer_id'] == customer_id]
        value_cash = str(df_search.cash_amount.to_list()).replace('[', '').replace(']', '')
        value_customer_id = str(df_search.customer_id.to_list()).replace('[', '').replace(']', '')
        value_date = str(df_search.ex_dividend_date.to_list()).replace('[', '').replace(']', '')
        value_money = str(df_search.currency.to_list()).replace('[', '').replace(']', '')

        builtins.customer_id = customer_id

        if value_customer_id == '':
            request_data = {"data": {"customer_id": 'customer not found'}}
        else:
            request_data = {"data": {"customer_id": value_customer_id,
                                     "value_cash": value_cash,
                                     "value_date": value_date,
                                     "value_money": value_money
                                     }
                            }
        return request_data, df_search
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
    
    str_to_dict = '{' + path + '}'
    json_request = json.dumps(str_to_dict)
    str_to_dict = json_request.replace("\'", "\"")
    print(str_to_dict)
    request_ = json.loads(str_to_dict)
    res = json.loads(request_)
    print(f"Request: {res}")
    path = res.get("path")
    
    path_document = path + 'document_validation.csv'
    df.to_csv(path_document, sep=',', encoding='utf-8', index=False)
    
    return f"write document in: {path_document}", "status: 200"


@app.route("/save/<request>/<path>", methods=['POST'])
def save_local(request, path):
    try:
        request, df = get_request(request)
        path = path.replace("_", "/")
        return df_to_local(df, path)
    except Exception as e:
        print(e)


@app.route("/main/<request>", methods=['POST'])
def main(request:dict):
    try:
        request, df = get_request(request)
        return str(request), "status: 200"
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port="4040")
