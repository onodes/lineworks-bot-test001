import os
import hashlib
import hmac
import base64
import json
import requests
import pprint
import boto3
import logging
from requests.models import Response
from requests.structures import CaseInsensitiveDict
from lineworks_bot.kintoneTools import GourmetMapLayout, GrourmetMap

API_ID = os.environ.get('API_ID')
SERVER_API_CONSUMER_KEY = os.environ.get('SERVER_API_CONSUMER_KEY')
BOT_NO = os.environ.get('BOT_NO')
SERVER_TOKEN = os.environ.get('SERVER_TOKEN') # access_token.pyで取得したToken
IMAGE_FILE_PATH = '/tmp/'
S3_BUCKET_NAME=os.environ.get('S3_BUCKET_NAME')
SUBDOMAIN = os.environ.get('KINTONE_SUBDOMAIN')
APP_ID= os.environ.get('KINTONE_APP_ID')
TOKEN = os.environ.get('KINTONE_TOKEN')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def check_request(body, signature):
    # signatureはリクエストヘッダーのX-Line-Signature

    # API_IDを秘密鍵として利用する
    secret_key = API_ID.encode('utf-8')
    payload = body.encode('utf-8')

    hash = hmac.new(
        secret_key,
        payload,
        hashlib.sha256
    ).digest()

    signature_from_body = base64.b64encode(hash)

    return signature_from_body == signature



def send_message(account_id, content):
    # メッセージを送信する。
    send_message_url = 'https://apis.worksmobile.com/' + API_ID + '/message/sendMessage/v2'
    
    headers = {
        'Content-Type' : 'application/json;charset=UTF-8',
        'ConsumerKey' : SERVER_API_CONSUMER_KEY,
        'Authorization' : "Bearer " + SERVER_TOKEN
    }
    
    payload = {
        'botNo': int(BOT_NO),
        'accountId': account_id,
        'content': content
    }
    
    payload_data = json.dumps(payload)

    try:
        res = requests.post(url=send_message_url, headers=headers, data=payload_data)
        pprint.pprint(res.json())
    except:
        return False
    
    if res.status_code == 200:
        return True
    else:
        return False



def get_image(resource_id, timeout=10):
    contents_request_url = 'http://storage.worksmobile.com/openapi/message/download.api'
    
    headers = {
        'ConsumerKey' : SERVER_API_CONSUMER_KEY,
        'Authorization' : "Bearer " + SERVER_TOKEN,
        'X-works-apiid': API_ID,
        'X-works-resource-id': resource_id
    }

    res = requests.get(contents_request_url, headers=headers)
    if res.status_code != 200:
        e = Exception("HTTP status: " + res.status_code)
        raise e

    return res.content

def create_kintone(account_id, filename):
    record = GourmetMapLayout()
    record.account_id = account_id
    record.filename = filename

    logger.info("kintone Subdomain is " + SUBDOMAIN)
    logger.info("kintone AppID is " + APP_ID)
    logger.info("kintone Token is " + TOKEN)
    logger.info("kintone account_id is " + account_id)
    logger.info("kintone filename is " + filename)

    grmm = GrourmetMap(SUBDOMAIN,APP_ID,TOKEN)
    res = grmm.create(record)
    if res.ok:
        logger.info("### KINTONE CREATE OK ###")
    else:
        logger.error("kintone error id is " + res.error.id)
        logger.error("kintone error message is " + res.error.message)
        logger.error("kintone error code is " + res.error.code)

def save_image(filename, image):
    with open(filename, "wb") as f:
        f.write(image)



def upload_file_s3(filename_fullpath, filename):
    s3_client = boto3.resource('s3')
    bucket = s3_client.Bucket(S3_BUCKET_NAME)
    bucket.upload_file(Filename=filename_fullpath, Key=filename)



def line_handler(req):
    account_id = req["source"]["accountId"]
    req_type = req["content"]["type"]

    if req_type == "text":
        content = req["content"]
        text = content["text"]
        send_text = account_id + "さん" + text + "！！"
        send_content = {
            "type": "text",
            "text": send_text            
        }

        if send_message(account_id, send_content):
            return True
        else:
            return False

    elif req_type == "image":
        content = req["content"]
        resource_id = content["resourceId"]
        
        image_b = get_image(resource_id)
        
        filename = "sample.PNG"
        filename_fullpath = IMAGE_FILE_PATH + filename
        save_image(filename_fullpath, image_b)
        upload_file_s3(filename_fullpath, filename)
        create_kintone(account_id, filename)
    else:
        return False


def lambda_handler(event, context):
    event = CaseInsensitiveDict(event)
    headers = event["headers"]
    body = event["body"]

    #不正なリクエストなら終了する
    #if not check_request(body, headers.get("x-works-signature")):
    #    return False

    req = json.loads(body)
    line_handler(req)

    res_body = {
        "code": 200,
        "message": "OK"
    }

    res = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(res_body)
    }

    return res