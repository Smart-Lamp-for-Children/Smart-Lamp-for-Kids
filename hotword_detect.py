import pvporcupine
import pyaudio
import struct

class PorcupineWakeWordDetector:
    def __init__(self, access_key, keyword_paths, model_path):
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=keyword_paths,
            model_path=model_path
        )
        self.audio_stream = None

    def start(self):
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

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
    access_key = "***"  # Picovoice访问密钥
    keyword_paths = ["C:\\Users\\**\\Downloads\\测测_zh_windows_v3_0_0\\测测_zh_windows_v3_0_0.ppn"]  # 关键词文件路径
    model_path = "C:\\Users\\**\\Downloads\\porcupine_params_zh.pv"  # 模型文件路径

    detector = PorcupineWakeWordDetector(access_key, keyword_paths, model_path)
    detector.start()

if __name__ == "__main__":
    main()