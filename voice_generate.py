import os
import base64
import uuid
import requests
from playsound import playsound
import config

def read_text_from_file(file_path):
    """读取指定路径的文本文件"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def text_to_speech(text, appid, access_token):
    """将文本合成语音并保存为 MP3 文件"""
    # header
    header = {"Authorization": f"Bearer;{access_token}"}

    # request
    request_json = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": "volcano_tts"
        },
        "user": {
            "uid": "388808087185088" 
        },
        "audio": {
            "voice_type": "BV700_streaming",
            "encoding": "mp3",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),  
            "text": text,
            "text_type": "plain",
            "operation": "query",
            "with_frontend": 1,
            "frontend_type": "unitTson"
        }
    }

    try:
        # api调用
        api_url = f"https://openspeech.bytedance.com/api/v1/tts"
        resp = requests.post(api_url, json=request_json, headers=header)

        # print
        print(f"响应内容: \n{resp.json()}")

        # 如果响应中包含音频数据，则保存为文件
        if "data" in resp.json():
            data = resp.json()["data"]

            # 确保 temporary_storage 文件夹存在
            folder_path = os.path.join(os.path.dirname(__file__), 'temporary_storage')
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # 保存音频文件
            file_path = os.path.join(folder_path, "output.mp3")
            with open(file_path, "wb") as file_to_save:
                file_to_save.write(base64.b64decode(data))  # 解码并保存音频

            print(f"音频已保存到 {file_path}")
            return file_path  # 返回文件路径

        else:
            print("响应中未包含音频数据。")
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None
    except Exception as e:
        print(f"程序发生异常: {e}")
        return None

def main():
    appid = config.xf_appid  # 讯飞 App ID
    access_token = config.xf_token  # 讯飞 Token
    voice_type = config.voice_type  # 音色
    test_text_path = config.test_text_path  # 文本文件路径

    try:
        # 读取文本文件内容
        text = read_text_from_file(test_text_path)

        # 合成语音
        file_path = text_to_speech(text, appid, access_token)

        if file_path:
            # 播放合成音频
            playsound(file_path)
        else:
            print("语音合成失败，无法播放音频。")

    except FileNotFoundError:
        print(f"文件 {test_text_path} 未找到!")
    except Exception as e:
        print(f"程序出现异常: {e}")

if __name__ == '__main__':
    main()
