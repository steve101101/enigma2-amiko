import os

def Titan(Screen):
    os.system('echo "Reboot Titan" > /dev/vfd')
    os.system('/bin/settitan.sh titan &')
