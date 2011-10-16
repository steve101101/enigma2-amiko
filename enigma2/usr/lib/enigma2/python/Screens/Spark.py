import os

def Spark(Screen):
    os.system('echo "Reboot Spark" > /dev/vfd')
    os.system('/bin/setspark.sh &')
