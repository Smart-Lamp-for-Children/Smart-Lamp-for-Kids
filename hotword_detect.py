import pvporcupine
import pyaudio
import struct
import os
import sys
# 获取上级目录的路径
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 将上级目录添加到 sys.path 中
sys.path.insert(0, parent_dir)
import config

class PorcupineWakeWordDetector:
    def __init__(self, access_key, keyword_paths, model_path):
        print("Initializing Porcupine...")
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=keyword_paths,
            model_path=model_path
        )
        print("Porcupine initialized.")
        self.audio_stream = None

    def start(self):
        print("Initializing PyAudio...")
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )
        print("PyAudio initialized.")

        print("Listening for wake word...")

        try:
            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    print("Wake word detected!")
                    break
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.audio_stream.close()
            self.porcupine.delete()

def main():
    access_key = config.hotword_access_key  # Picovoice访问密钥
    keyword_paths = config.hotword_key_word_path  # 关键词文件路径
    model_path = config.hotword_model_path  # 模型文件路径

    detector = PorcupineWakeWordDetector(access_key, keyword_paths, model_path)
    print (detector.porcupine.frame_length)
    detector.start()

if __name__ == "__main__":
    main()
