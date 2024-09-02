import os
import pyaudio
import wave
import io
import struct
import base64
import json
from time import sleep
from gtts import gTTS

# 自定义模块
import chat
import voice_generate
import voice_recognize
import hotword_detect
import silence_detect

# 设置api参数和模型文件地址
access_key = "***"
keyword_paths = ["***"]
model_path = "***"
stt_access_token = "***"
tts_access_token = "***"

# 初始化唤醒词检测器
detector = hotword_detect.PorcupineWakeWordDetector(access_key, keyword_paths, model_path)

# 初始化音频流
pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024
)

def playsound(filename:str):
    #TO DO
    os.system('aplay -Dhw:0,0 '+filename)
 
# 生成并播放语音消息的函数
# def play_audio_message(message, filename="temp.mp3"):
#     tts = gTTS(text=message, lang='zh')  # 使用中文语音生成，可以改为其他语言
#     tts.save(filename)
#     playsound(filename)
#     os.remove(filename)  # 播放完后删除临时文件


def record_audio():
    maxnothing = 100
    sdv = silence_detect.Vad()
    frames = []
    f = io.BytesIO()
    count = 0
    os.system(r'powershell -c (New-Object Media.SoundPlayer "C:\Users\**\Downloads\提示音.wav").PlaySync();')

    sleep(1)
################################################################
#                                                              #
#               Audio Output                                   #
#                                                              #
################################################################
    print("请说话，我在听着呢。")

    num=0
    while True:

        bytes_obv = stream.read(1024, exception_on_overflow=False)
        sdv.check_ontime(num,bytes_obv)
        print(num)
        num = num + 1

        if sdv.cur_status == 2:
            frames.append(bytes_obv)
        elif sdv.cur_status == 3:
            with wave.open(f, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(frames))

################################################################
#                                                              #
#               Audio Output                                   #
#                                                              #
################################################################
            print("好的，我明白了。")
            os.system(r'powershell -c (New-Object Media.SoundPlayer "C:\Users\**\Downloads\提示音.wav").PlaySync();')
            return True, b''.join(frames)
        else:
            count += 1
            if count == maxnothing:
################################################################
#                                                              #
#               Audio Output                                   #
#                                                              #
################################################################
                print("对不起，我没有听清楚您的指令。")
                os.system(r'powershell -c (New-Object Media.SoundPlayer "C:\Users\**\Downloads\提示音.wav").PlaySync();')
                return False, b''.join(frames)

def save_audio(frames, file_path):
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(frames)

def main():
    while True:
        # 1. 唤醒词检测
        detector.start()
        
        # 2. 录制用户的语音输入
        _, recorded_audio = record_audio()
        audio_file_path = "recorded_audio.wav"
        save_audio(recorded_audio, audio_file_path)
        
        # 3. 将录音文件转换并进行语音识别
        converted_audio_path = "converted_audio.wav"
        voice_recognize.convert_audio(audio_file_path, converted_audio_path)

        with open(converted_audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        recognized_text = voice_recognize.stt(audio_data, stt_access_token)
        print(f"识别的文本: {recognized_text}")
        
        # 4. 使用自然语言处理模块理解用户的意图
        nlp_result = chat.response(recognized_text)
        print(f"NLU结果: {nlp_result}")

        # 5. 将NLP的回复内容转换为语音
        if nlp_result["is_understood"]:
            voice_generate.text_to_speech(nlp_result["response"], tts_access_token)
            playsound('output.mp3')
        else:
            print("对不起，我没有理解你的意思。")
            playsound('error_sound.wav')
        
        sleep(1)  # 暂停一段时间再继续等待唤醒词

if __name__ == "__main__":
    main()