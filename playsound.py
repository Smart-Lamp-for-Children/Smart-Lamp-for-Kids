import os
def playsound(sound_path):
    # os.system("aplay -c 2 -Dhw:0,0 " + sound_path) 
    os.system("cvlc --play-and-exit " + sound_path) 