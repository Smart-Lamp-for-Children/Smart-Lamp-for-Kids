import os
import pyaudio
import wave
import io
import struct
import base64
import json
import glob #用于检测并清空temporary_storage中的文件
from playsound import playsound
from time import sleep

# 自定义模块
import chat
import voice_generate
import voice_recognize
import hotword_detect
import silence_detect

import sys
# 获取上级目录的路径
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 将上级目录添加到 sys.path 中
sys.path.insert(0, parent_dir)
import config
# 设置api参数和模型文件地址
hotword_access_key = config.hotword_access_key
keyword_paths = config.hotword_key_word_path
model_path = config.hotword_model_path
voice_generate_app_id = config.xf_appid
voice_access_token = config.xf_token

# 初始化音频流
pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024
)

def record_audio():
    maxnothing = 100
    sdv = silence_detect.Vad()
    frames = []
    count = 0
    #playsound(config.prompt_tone_path) ###音频播放(可能需要改动)(在windows上没跑通，原因不明) #去除不影响功能，可考虑不在录音开始和结束时播放提示音

    sleep(1)
    print('请开始说话')

    num=0
    while True:

        bytes_obv = stream.read(1024, exception_on_overflow=False)
        sdv.check_ontime(num,bytes_obv)
        num = num + 1

        if sdv.cur_status == 2:
            frames.append(bytes_obv)
            continue
        elif sdv.cur_status == 0:
            count += 1
            if count >= maxnothing:
                break
        break
    print('done')
    #playsound(config.prompt_tone_path) ###音频播放(可能需要改动)(在windows上没跑通，原因不明) #去除不影响功能，可考虑不在录音开始和结束时播放提示音
    
    return b''.join(frames)

def save_audio(frames, file_path):
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(frames)

def main():
    while True:
        # 1. 唤醒词检测
        detector = hotword_detect.PorcupineWakeWordDetector(hotword_access_key, keyword_paths, model_path)
        detector.start()
        
        # 2. 录制用户的语音输入
        recorded_audio = record_audio()
        audio_file_path = "temporary_storage/recorded_audio.wav"
        save_audio(recorded_audio, audio_file_path)
        
        # 3. 将录音文件转换并进行语音识别
        converted_audio_path = "temporary_storage/converted_audio.wav"
        voice_recognize.convert_audio(audio_file_path, converted_audio_path)

        with open(converted_audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        recognized_text = voice_recognize.stt(audio_data, voice_access_token)
        print(f"识别的文本: {recognized_text}")
        
        # 4. 使用自然语言处理模块理解用户的意图
        nlp_result = chat.response(recognized_text)
        print(f"NLU结果: {nlp_result}")

        # 5. 将NLP的回复内容转换为语音
        if nlp_result["is_understood"]:
            voice_generate.text_to_speech(nlp_result["response"], voice_generate_app_id , voice_access_token)
            playsound(config.output_sound_path) ###音频播放(可能需要改动)(此处可正常运行)
        else:
            print("对不起，我没有理解你的意思。")
            playsound(config.error_sound_path) ###音频播放(可能需要改动)(此处可正常运行)
        
        # [os.remove(file) for file in glob.glob("temporary_storage/*")]  ####检测并清空temporary_storage中的文件，可以考虑删除并在main中与图像模块集成
        
        sleep(1)  # 暂停一段时间再继续等待唤醒词

if __name__ == "__main__":
    main()
