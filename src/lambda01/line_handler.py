import os
import hashlib
import hmac
import base64

API_ID = os.environ.get("API_ID")
SERVER_LIST_PRIVATEKEY = os.environ.get("SERVER_LIST_PRIVATEKEY")
BOT_NO = os.environ("BOT_NO")
SERVER_TOKEN = os.environ("SERVER_TOKEN")

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
        'botNo': int(BOTNO),
        'accountId': account_id,
        'content': content
    }