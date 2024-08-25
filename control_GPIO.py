import RPi.GPIO as GPIO
import threading
import time
#设置引脚编号格式，参见raspi_PIN.png，这里采用GPIO num对应相应编号
GPIO.setmode(GPIO.BCM)

#GPIO函数会在停止后立刻结束输出，所以均采用threading包采用后台线程运行

################################################################
#                                                              #
#                   TO BE TESTED                               #
#                                                              #
################################################################
def PWM(pwm_pin_num:int | list[int] | tuple[int],#选择支持pwm的pin
        freq,
        stop_event,increase_event,decrease_event,
        dc = 50.0):
    GPIO.setup(pwm_pin_num, GPIO.OUT)
    try:
        p_list=[]
        if isinstance(pwm_pin_num, list | tuple):
            for pin in pwm_pin_num:
                p_list.append(GPIO.PWM(pin,freq))
        else:
            p_list.append(GPIO.PWM(pwm_pin_num,freq))
        for p in p_list:
            p.start(dc)
        while not stop_event.is_set():
            if increase_event.is_set():
                dc+=10
                for p in p_list:
                    p.ChangeDutyCycle(dc)
            if decrease_event.is_set():
                dc-=10
                for p in p_list:
                    p.ChangeDutyCycle(dc)
            time.sleep(0.2)
    finally:
        for p in p_list:
            p.stop()

if __name__ =="__main__":
    stop_event = threading.Event()
    increase_event = threading.Event()
    decrease_event = threading.Event()
    
    background_thread = threading.Thread(target=PWM, args=(12,50,stop_event,increase_event,decrease_event))
    
    background_thread.start()
    for i in range(2):
        print("主线程正在执行其他任务...")
        time.sleep(2)
    stop_event.set()
    background_thread.join()
    print("主线程结束")
    GPIO.cleanup()