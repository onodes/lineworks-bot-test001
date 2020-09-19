import os
import datetime
import jwt
import requests
import urllib
import json

API_ID = os.environ.get("API_ID")
SERVER_LIST_ID = os.environ.get("SERVER_LIST_ID") 
SERVER_LIST_PRIVATEKEY = os.environ.get("SERVER_LIST_PRIVATEKEY")

def create_jwt():
    current_time = datetime.datetime.now().timestamp()

    iss = SERVER_LIST_ID
    iat = current_time
    exp = current_time + 3600 #max 3600
    secret = SERVER_LIST_PRIVATEKEY

    json_claim_set = {
           'iss': iss,
           'iat': iat,
           'exp': exp
        }

    jwttoken = jwt.encode(
        json_claim_set,
        secret,
        algorithm='RS256')

    return jwttoken.decode("utf-8")

def create_server_token(jwttoken):
    url = 'https://authapi.worksmobile.com/b/' + API_ID + '/server/token'
    
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    payload = {
        "grant_type" : urllib.parse.quote("urn:ietf:params:oauth:grant-type:jwt-bearer"),
        "assertion" : jwttoken
    }

    req = requests.post(url=url, data=payload, headers=headers)
    
    body = json.loads(req.text)
    server_token = body["access_token"]
    
    return server_token

if __name__ == "__main__":
    jwttoken = create_jwt()
    server_token = create_server_token(jwttoken)
    print(server_token)

