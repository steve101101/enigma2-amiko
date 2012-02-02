import os
from Screens.Screen import Screen

class MountHDD(Screen):
	skin = """
		<screen name="MountHDD" position="center,center" size="610,410" title="MountHDD" >
		</screen>"""
		
def MountHDD(Screen):
    os.system('echo "MountHDD" > /dev/vfd')
    os.system('/bin/MountHDD &')

class FormatHDD(Screen):
	skin = """
		<screen name="FormatHDD" position="center,center" size="610,410" title="FormatHDD" >
		</screen>"""    
def FormatHDD(Screen):
    os.system('echo "FormatHDD" > /dev/vfd')
    os.system('/bin/FormatHDD &')

