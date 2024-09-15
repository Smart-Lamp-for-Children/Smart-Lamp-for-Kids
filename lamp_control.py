import control_GPIO as GPIO

class LampControl:
    def __init__(self, on: bool = False):
        # 初始化PWM控制器。

        # :PWM: 用于控制灯的亮度
        # :on_off: 用于控制灯的开关
        self.brightness = 50.0
        self.freq = 1000
        self.on = on
        self.PWM = GPIO.PWM(12,self.freq,self.brightness)
        self.on_off = GPIO.Output(6,self.on)


        self.PWM.start()
        self.on_off.set_output()
        
    def change_brightness(self, brightness: float):
        # 改变灯的亮度
        self.brightness = brightness
        if self.brightness < 0:
            self.brightness = 0
        if self.brightness > 100:
            self.brightness = 100
        self.PWM.change_dc(self.brightness)

    def change_on_off(self, on: bool):
        # 改变灯的开关状态
        self.on = on
        self.on_off.output = self.on
        self.on_off.set_output()
