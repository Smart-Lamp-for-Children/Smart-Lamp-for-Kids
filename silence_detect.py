# −∗− coding:utf−8 −∗−
import os
import wave
from time import sleep
import numpy as np
import pyaudio
import matplotlib.pyplot as plt

import config

SUCCESS = 0
FAIL = 1

audio = pyaudio.PyAudio()
audio2 = ""
stream2 = ""
FORMAT = pyaudio.paInt16
stream = audio.open(format=FORMAT,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024)

# 需要添加录音互斥功能，某些功能开启的时候录音暂时关闭
def ZCR(curFrame):
    # 过零率
    tmp1 = curFrame[:-1]
    tmp2 = curFrame[1:]
    signs = (tmp1 * tmp2 <= 0)
    diffs = (tmp1 - tmp2) > 0.02
    zcr = np.sum(signs * diffs)
    return zcr

def STE(curFrame):
    # 短时能量
    amp = np.sum(np.abs(curFrame))
    return amp

class Vad(object):
    def __init__(self):
        # 初始短时能量高门限
        self.amp1 = 940
        # 初始短时能量低门限
        self.amp2 = 120
        # 初始短时过零率高门限
        self.zcr1 = 30
        # 初始短时过零率低门限
        self.zcr2 = 2
        # 允许最大静音长度
        self.maxsilence = 45  # 允许换气的最长时间
        # 语音的最短长度
        self.minlen = 40  # 过滤小音量
        # 偏移值
        self.offsets = 40
        self.offsete = 40
        # 能量最大值
        self.max_en = 20000
        # 初始状态为静音
        self.status = 0
        self.count = 0
        self.silence = 0
        self.frame_len = 1024
        self.frame_inc = 128
        self.cur_status = 0
        self.frames = []
        # 数据开始偏移
        self.frames_start = []
        self.frames_start_num = 0
        # 数据结束偏移
        self.frames_end = []
        self.frames_end_num = 0
        # 缓存数据
        self.cache_frames = []
        self.cache = ""
        # 最大缓存长度
        self.cache_frames_num = 0
        self.end_flag = False
        self.wait_flag = False
        self.on = True
        self.callback = None
        self.callback_res = []
        self.callback_kwargs = {}

        self.frames = []
        self.x = []
        self.y = []

    def check_ontime(self, num,cache_frame):  # self.cache的值为空 self.cache_frames的数量为744
        global audio2, stream2
        wave_data = np.frombuffer(cache_frame, dtype=np.int16)  # 这里的值竟然是256
        wave_data = wave_data * 1.0 / self.max_en  # max_en为20000
        data = wave_data[np.arange(0, self.frame_len)]  # 取前frame_len个值这个值为256
        # speech_data = self.cache_frames.pop(0) # 删除第一个元素，并把第一个元素给 speech_data , 长度为256
        # 获得音频过零率
        zcr = ZCR(data)
        # 获得音频的短时能量, 平方放大
        amp = STE(data) ** 2
        # 返回当前音频数据状态
        res = self.speech_status(amp, zcr)

        self.cur_status = res

        if res == 2:
            # 开始截取音频
            if not audio2:
                audio2 = pyaudio.PyAudio()
                stream2 = audio2.open(format=FORMAT,
                                      channels=1,
                                      rate=16000,
                                      input=True,
                                      frames_per_buffer=1024)
            stream_data = stream2.read(1024)
            wave_data = np.frombuffer(stream_data, dtype=np.int16)
            print(num, "正在说话ing...")
            self.frames.append(stream_data)

        if res == 3 and len(self.frames) > 25:
            wf = wave.open(config.silence_input_path + str(num) + ".wav", 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(audio2.get_sample_size(FORMAT))
            wf.setframerate(16000)
            wf.writeframes(b"".join(self.frames))
            self.frames = []
            stream2.stop_stream()
            stream2.close()
            audio2.terminate()
            audio2 = ""
            stream2 = ""
            wf.close()

    def speech_status(self, amp, zcr):
        status = 0
        # 0=静音，1=可能开始, 2=确定进入语音段, 3=语音结束
        if self.cur_status in [0, 1]:  # 如果在静音状态或可能的语音状态，则执行下面操作
            # 确定进入语音段
            if amp > self.amp1 or zcr > self.zcr1:  # 超过最大短时能量门限了
                status = 2
                self.silence = 0
                self.count += 1
            # 可能处于语音段，能量处于浊音段，过零率在清音或浊音段
            elif (amp > self.amp2 or zcr > self.zcr2) and (amp < self.amp1):
                status = 2
                self.count += 1
            # 静音状态
            else:
                status = 0
                self.count = 0
                self.silence = 0
        # 2=语音段
        elif self.cur_status == 2:
            # 保持在语音段，能量处于浊音段，过零率在清音或浊音段
            if (amp > self.amp2 or zcr > self.zcr2) and (amp < self.amp1):
                self.count += 1
                status = 2
                print(amp)
                print(zcr)
            # 语音将结束
            else:
                # 静音还不够长，尚未结束
                self.silence += 1
                if self.silence < self.maxsilence:
                    self.count += 1
                    status = 2
                # 语音长度太短，认为是噪声
                elif self.count < self.minlen:
                    status = 0
                    self.silence = 0
                    self.count = 0
                # 语音结束
                else:
                    status = 3
                    self.silence = 0
                    self.count = 0
        return status

class FileParser(Vad):
    def __init__(self):
        self.block_size = 1024
        Vad.__init__(self)

if __name__ == "__main__":
    stream_test = FileParser()
    num = 0
    while True:
        byte_obj = stream.read(1024)
        stream_test.check_ontime(num, byte_obj)
        print(num)
        num = num + 1