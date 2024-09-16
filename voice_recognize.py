from pydub import AudioSegment
import requests
import base64
import json
import os

import config

def convert_audio(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(output_file, format="wav")

def stt(audio_data, access_token):
    stt_url = "https://vop.baidu.com/server_api"

    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    params = {
        "format": "wav",
        "rate": 16000,
        "channel": 1,
        "cuid": "102279035",
        "token": access_token,
        "speech": audio_base64,
        "len": len(audio_data)
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(stt_url, headers=headers, data=json.dumps(params))
        response.raise_for_status()
        result = response.json()
        if result['err_no'] == 0:
            return result['result'][0]
        else:
            return "Error: " + result['err_msg']
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def main():
    input_audio_file_path = "test.wav"
    converted_audio_file_path = "converted_test.wav"
    access_token = config.voice_access_token

    convert_audio(input_audio_file_path, converted_audio_file_path)

    try:
        with open(converted_audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        result = stt(audio_data, access_token)
        print("识别结果:", result)
    except Exception as e:
        print(f"处理过程中出错: {e}")

if __name__ == "__main__":
    main()