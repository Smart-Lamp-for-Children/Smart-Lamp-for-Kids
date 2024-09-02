import RPi.GPIO as GPIO
import threading
import time
#设置引脚编号格式，参见raspi_PIN.png，这里采用GPIO num对应相应编号
GPIO.setmode(GPIO.BCM)



################################################################
#                                                              #
#               GPIO CONTROL CLASS                             #
#                                                              #
################################################################
#                                                              #
#                   TO BE TESTED                               #
#                                                              #
################################################################

#GPIO.PWM函数会在停止后立刻结束输出，所以采用threading包采用后台线程运行
class PWM:
    def __init__(self, pwm_pin_num: int | list[int] | tuple[int], freq: int, dc: float = 50.0):
        # 初始化PWM控制器。

        # :param pwm_pin_num: 支持PWM的Pin编号，可以是单个数字、列表或元组。
        # :param freq: PWM的频率。
        # :param dc: 初始占空比（默认为50.0）。范围为0.0到100.0。

        self.pwm_pin_num = pwm_pin_num
        self.freq = freq
        self.dc = dc
        self.stop_event = threading.Event()
        self.dc_change_event = threading.Event()
        self.thread = None
        self.p_list = []

        # 设置GPIO引脚并初始化PWM对象
        GPIO.setup(pwm_pin_num, GPIO.OUT)
        if isinstance(pwm_pin_num, (list, tuple)):
            for pin in pwm_pin_num:
                self.p_list.append(GPIO.PWM(pin, freq))
        else:
            self.p_list.append(GPIO.PWM(pwm_pin_num, freq))

    def _run(self):
        #后台线程执行的PWM控制逻辑。
        try:
            for p in self.p_list:
                p.start(self.dc)
            while not self.stop_event.is_set():
                if self.dc_change_eventis_set():
                    for p in self.p_list:
                        p.ChangeDutyCycle(self.dc)
                    self.dc_change_event.clear()

                time.sleep(0.2)
        finally:
            for p in self.p_list:
                p.stop()
            GPIO.cleanup()  # 清理GPIO设置

    def start(self):
        #启动PWM控制线程。
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run)
            self.thread.start()
            print("PWM控制线程启动")

    def stop(self):
        #停止PWM控制线程。
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join()
            print("PWM控制线程停止")

    def change_dc(self,dc: float):
        #更改占空比

        if dc<0.0 :
            dc = 0.0
        elif dc>100.0:
            dc = 100.0
        
        self.dc = dc
        self.dc_change_event.set()


class Output:
    def __init__(self, out_pin_num: int | list[int] | tuple[int], output: bool | list[bool] | tuple[bool]):
        # 初始化GPIO输出控制器。
        # :param out_pin_num: 选择输出的Pin编号，可以是单个数字、列表或元组。
        # :param output: 输出状态，单个布尔值或布尔值的列表/元组。

        self.out_pin_num = out_pin_num
        self.output = output

        # 参数类型和长度检查
        if isinstance(out_pin_num, int) and isinstance(output, (list, tuple)):
            raise ValueError("GPIO Output Error: 'output' 类型应与 'out_pin_num' 类型一致，都是单个值。")
        if isinstance(output, (list, tuple)) and len(output) != len(out_pin_num):
            raise ValueError("GPIO Output Error: 'output' 和 'out_pin_num' 的长度应一致。")
      # 设置GPIO模式为BOARD
        self._setup_pins()

    def _setup_pins(self):
        # 设置GPIO引脚为输出模式。
        GPIO.setup(self.out_pin_num, GPIO.OUT)

    def set_output(self):
        #设置GPIO引脚的输出状态
        GPIO.output(self.out_pin_num, self.output)

################################################################
#                                                              #
#                   TO BE DONE                                 #
#                                                              #
################################################################
# class Input:
    #TO DO


################################################################
#                                                              #
#                       TEST FUNCTION                          #
#                                                              #
################################################################

#测试程序，采用后台线程运行，前台线程通过各种event控制
def PWM_test():
    dc=50.0
    pwm = PWM(12, dc)
    pwm.start()

    # 提高占空比
    for i in range(5):
        time.sleep(2)
        dc += 10.0
        pwm.change_dc(dc)
        print(f"增加后的占空比: {pwm.dc}%")
    
    time.sleep(2)

    dc=50.0
    # 降低占空比
    for i in range(15):
        time.sleep(2)
        dc -= 10.0
        pwm.change_dc(dc)
        print(f"减少后的占空比: {pwm.dc}%")

    time.sleep(2)
    dc = 80.0
    pwm.change_dc(dc)

    # 停止PWM
    pwm.stop()
    print("测试结束")

def Output_test():

    try:
        # GPIO 6 输出高电平
        output_controller = Output(6, True)
        output_controller.set_output()
        print("GPIO 6 设置为高电平")
        time.sleep(5)

        # GPIO 6 输出低电平
        output_controller.output = False
        output_controller.set_output()
        print("GPIO 6 设置为低电平")
        time.sleep(5)

        # GPIO 5,6 输出高电平
        output_controller.out_pin_num = [5, 6]
        output_controller.output = True
        output_controller.set_output()
        print("GPIO 5,6 设置为高电平")
        time.sleep(5)

        # GPIO 5,6 分别输出高电平和低电平
        output_controller.output = [True, False]
        output_controller.set_output()
        print("GPIO 5 设置为高电平, GPIO 6 设置为低电平")
        time.sleep(5)

    finally:
        # 清理GPIO设置
        GPIO.cleanup()
        print("GPIO 清理完成")

if __name__ =="__main__":
    PWM_test()
    GPIO.cleanup()
    Output_test()
    GPIO.cleanup()