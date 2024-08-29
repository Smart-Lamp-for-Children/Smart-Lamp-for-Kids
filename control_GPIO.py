import RPi.GPIO as GPIO
import threading
import time
#设置引脚编号格式，参见raspi_PIN.png，这里采用GPIO num对应相应编号
GPIO.setmode(GPIO.BCM)

#GPIO函数会在停止后立刻结束输出，所以均采用threading包采用后台线程运行

################################################################
#                                                              #
#               GPIO CONTROL FUNCTION                          #
#                                                              #
################################################################
#                                                              #
#                   TO BE TESTED                               #
#                                                              #
################################################################
def PWM(pwm_pin_num:int | list[int] | tuple[int],#选择支持pwm的pin
        freq,
        stop_event,increase_event,decrease_event,#后两个event每0.2s检测一次
        dc = 50.0): #dc为方波的占空比
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
                if dc <= 90:
                    dc+=10
                else :
                    dc =100
                for p in p_list:
                    p.ChangeDutyCycle(dc)
            if decrease_event.is_set():
                if dc >=10:
                    dc-=10
                else :
                    dc =0
                for p in p_list:
                    p.ChangeDutyCycle(dc)
            time.sleep(0.2)
    finally:
        for p in p_list:
            p.stop()

def Output(out_pin_num: int | list[int] | tuple[int],#选择output pin
           output:bool | list[bool] | tuple[bool]):#out_pin为单个时，out必须为单个
    GPIO.SETUP(out_pin_num,GPIO.OUT)

    #参数类型不匹配时报错
    if isinstance(out_pin_num,int) and isinstance(output, list | tuple):
        print("GPIO Output Error:the type of  \'output\' should be consistant with \'out_pin_num\' ")
        return

    #经过检测后out为列表/元组时out_pin必然为列表/元组
    if isinstance(output , list | tuple) :
        #长度不一致时报错
        if len(output) != len(out_pin_num) :
            print("GPIO Output Error:the length of  \'output\' should be consistant with \'out_pin_num\' ")
            return
        #依次给对应端口赋予对应端口号
    GPIO.out(out_pin_num,output)

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
    stop_event = threading.Event()
    increase_event = threading.Event()
    decrease_event = threading.Event()
    
    background_thread = threading.Thread(target=PWM, args=(12,50,stop_event,increase_event,decrease_event))

    #启动后台线程
    background_thread.start()
    print("后台线程启动")

    dc = 50
    
    #提高占空比
    for i in range(5):
        dc += 10
        print(dc)#正常运行的话dc超过100后占空比不再改变，维持100
        increase_event.set()
        time.sleep(2)
    
    dc = 100
    print(dc)
    time.sleep(2)

    #降低占空比
    for i in range(15):
        dc -= 10
        print(dc)#正常运行的话dc低于后占空比不再改变，维持0
        decrease_event.set()
        time.sleep(2)

    #结束测试
    stop_event.set()
    background_thread.join()
    print("主线程结束")

def Output_test():

    #GPIO 6 输出高电平
    background_thread = threading.Thread(target= Output, args=(6,True))
    background_thread.start()
    print("后台线程启动")
    time.sleep(5)
    background_thread.join()

    #GPIO 6 输出低电平
    background_thread = threading.Thread(target= Output, args=(6,False))
    background_thread.start()
    print("后台线程启动")
    time.sleep(5)
    background_thread.join()

    #GPIO 5,6 输出高电平
    background_thread = threading.Thread(target= Output, args=([5,6],True))
    background_thread.start()
    print("后台线程启动")
    time.sleep(5)
    background_thread.join()

    #GPIO 5,6 输出低电平
    background_thread = threading.Thread(target= Output, args=([5,6],[True,False]))
    background_thread.start()
    print("后台线程启动")
    time.sleep(5)
    background_thread.join()

if __name__ =="__main__":
    PWM_test()
    GPIO.cleanup()
    Output_test()
    GPIO.cleanup()