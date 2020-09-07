import os
import hashlib
import hmac
import base64
import json
import requests
from requests.structures import CaseInsensitiveDict

API_ID = os.environ.get("API_ID")
SERVER_API_CONSUMER_KEY = os.environ.get("SERVER_API_CONSUMER_KEY")
BOT_NO = os.environ.get("BOT_NO")
SERVER_TOKEN = os.environ.get("SERVER_TOKEN") # access_token.pyで取得したToken

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
        'consumerKey' : SERVER_API_CONSUMER_KEY,
        'Authorization' : "Bearer " + SERVER_TOKEN
    }
    
    payload = {
        'botNo': int(BOT_NO),
        'accountId': account_id,
        'content': content
    }
    
    payload_data = json.dumps(payload)

    try:
        req = requests.post(url=send_message_url, headers=headers, data=payload_data)
    except:
        return False
    
    if req.status_code == 200:
        return True
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
    account_id = req["source"]["accountId"]

    res_content = {
        "type": "text",
        "text": "テキスト"
    }

    if req["type"] == "message":
        content = req["content"]
        text = content["text"]
        res_text = text + "！！"
        res_content = {
            "type": "text",
            "text": res_text            
        }
    
    send_message(account_id, res_content)

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