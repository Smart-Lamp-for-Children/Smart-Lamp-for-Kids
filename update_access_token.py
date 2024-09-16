import requests

import config

def get_access_token(api_key, secret_key):
    """通过API Key和Secret Key获取Access Token"""
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    
    response = requests.post(url, params=params)
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info.get("access_token")
        if access_token:
            print("Access Token 获取成功:", access_token)
            return access_token
        else:
            print("获取 Access Token 失败:", token_info)
    else:
        print("请求失败，状态码:", response.status_code)

# 替换为你自己的API Key和Secret Key
api_key = config.voice_api_key
secret_key = config.voice_secret_key

# 获取Access Token
access_token = get_access_token(api_key, secret_key)