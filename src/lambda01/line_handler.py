import os
import hashlib
import hmac
import base64

API_ID = os.environ.get("API_ID")

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
    
    