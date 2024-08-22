import requests

def read_text_from_file(file_path):
    """读取指定路径的文本文件"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def text_to_speech(text, access_token):
    """将文本合成语音并保存为 MP3 文件"""
    # 语音合成 API URL
    url = "https://tsn.baidu.com/text2audio"

    # 请求参数
    params = {
        "tex": text,                       # 要合成的文本
        "lan": "zh",                      # 语言，中文为 zh
        "cuid": "1234567",                # 用户 ID，可以是任意字符串
        "ctp": 1,                         # 客户端类型，固定为 1
        "tok": access_token,              # Access Token
        "vol": 5,                         # 音量，取值范围 0-9
        "per": 0,                         # 发音人，0为女声，1为男声
        "spd": 5,                         # 语速，取值范围 0-9
        "pit": 5                          # 音调，取值范围 0-9
    }

    response = requests.post(url, data=params)

    if response.status_code == 200:
        # 保存音频文件
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        print("语音合成成功，文件已保存为 output.mp3")
    else:
        print("语音合成失败:", response.text)

def main():
    access_token = "***"  # Access Token
    text_file_path = r"C:\Users\**\Downloads\text_to_speak.txt"  # 文本文件路径

    # 读取文本文件内容
    text = read_text_from_file(text_file_path)

    # 合成语音
    text_to_speech(text, access_token)

if __name__ == '__main__':
    main()