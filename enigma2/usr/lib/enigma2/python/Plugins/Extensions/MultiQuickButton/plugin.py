# Multi QuickButton Rel. 2.4
# from Emanuel CLI 2009
#
# ***special thanks*** to Dr.Best & AliAbdul ;-)

from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.ChannelSelection import ChannelSelection
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigYesNo
from Screens.MessageBox import MessageBox
from QuickButtonXML import QuickButtonXML
from MultiQuickButton import MultiQuickButton, QuickButton
from  Screens.InfoBarGenerics import InfoBarPlugins
import xml.sax.xmlreader
import os.path


baseInfoBarPlugins__init__ = None
baserunPlugin = None
StartOnlyOneTime = False
line = "------------------------------------------------------------------"

def autostart(reason, **kwargs):
	if reason == 0:
		if config.plugins.QuickButton.enable.value:
			print line
			print "[MultiQuickButton] enabled: ",config.plugins.QuickButton.enable.getValue()
			print line
			global baseInfoBarPlugins__init__, baserunPlugin
			if "session" in kwargs:
				session = kwargs["session"]
				if baseInfoBarPlugins__init__ is None:
					baseInfoBarPlugins__init__ = InfoBarPlugins.__init__
				if baserunPlugin is None:
					baserunPlugin = InfoBarPlugins.runPlugin	
				InfoBarPlugins.__init__ = InfoBarPlugins__init__
				InfoBarPlugins.runPlugin = runPlugin
				InfoBarPlugins.checkQuickSel = checkQuickSel
				InfoBarPlugins.askForQuickList = askForQuickList
				InfoBarPlugins.getQuickList = getQuickList
				InfoBarPlugins.execQuick = execQuick
				InfoBarPlugins.quickSelectGlobal = quickSelectGlobal

		else:
			print line
			print "[MultiQuickButton] disabled"
			print line
	else:
		print "[MultiQuickButton] checking keymap.xml..."
		import os
		if os.path.exists("/usr/share/enigma2/keymap.xml"):
			com = "/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/keymap_patch.sh"
			os.system(com)

def InfoBarPlugins__init__(self):
	global StartOnlyOneTime
	if not StartOnlyOneTime:
		StartOnlyOneTime = True

		self["QuickButtonActions"] = MQBActionMap(["QuickButtonActions"],
			{
				"red": self.quickSelectGlobal,
				"green": self.quickSelectGlobal,
				"yellow": self.quickSelectGlobal,
				"blue": self.quickSelectGlobal,
				"vformat": self.quickSelectGlobal,
				"picasa": self.quickSelectGlobal,
				"shoutcast": self.quickSelectGlobal,
				"youtube": self.quickSelectGlobal,
				"find": self.quickSelectGlobal,
				"f1": self.quickSelectGlobal,
				"f2": self.quickSelectGlobal,
				"f3": self.quickSelectGlobal,
				"f4": self.quickSelectGlobal,
				"sleep": self.quickSelectGlobal,
				"spark": self.quickSelectGlobal,
				"tvradio": self.quickSelectGlobal,
				"sat": self.quickSelectGlobal,
				"fav": self.quickSelectGlobal,
				"info": self.quickSelectGlobal,
				"epg": self.quickSelectGlobal,
				"file": self.quickSelectGlobal,
				"playmode": self.quickSelectGlobal,
				"usb": self.quickSelectGlobal,
				"recall": self.quickSelectGlobal,
				"tvsat": self.quickSelectGlobal,
			})
	else:
		InfoBarPlugins.__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.runPlugin = InfoBarPlugins.runPlugin
		InfoBarPlugins.quickSelectGlobal = None
	baseInfoBarPlugins__init__(self)

def runPlugin(self, plugin):
	baserunPlugin(self,plugin)

def checkQuickSel(self, path):
	list = None
	button = os.path.basename(path)[12:-4]
	try:
		menu = xml.dom.minidom.parse(path)
		db = QuickButtonXML(menu)
		list = db.getSelection()
	except Exception, e:
		self.session.open(MessageBox,("XML " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)
		print "[MultiQuickbutton] ERROR: ",e
		
	if list <> None:
		if len(list) == 1:
			self.execQuick(list[0])

		elif len(list) > 1:
			self.session.openWithCallback(self.askForQuickList,ChoiceBox,"Multi Quickbutton Menu %s" % (button), self.getQuickList(list))
			
		else:
			if os.path.exists(path):
				self.session.open(QuickButton, path, ('Quickbutton: Key ' + button))
			else:
				self.session.open(MessageBox,("file %s not found!" % (path)),  MessageBox.TYPE_ERROR)
		
def askForQuickList(self, res):
	if res is None:
		pass
	else:
		self.execQuick(res)

def getQuickList(self, list):
	quickList = []
	for e in list:
		quickList.append((e))
		
	return quickList
	
def execQuick(self,entry):
	if entry <> None:
		if entry[3] <> "":
			try:
				module_import = "from " + entry[3] + " import *"
				exec(module_import)
				if entry[4] <> "":
					try:
						screen = "self.session.open(" + entry[4] + ")"
						exec(screen)
					except Exception, e:
						self.session.open(MessageBox,("Screen " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)
						
			except Exception, e:
				self.session.open(MessageBox,("Module " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)
			
		if entry[5] <> "":
			try:
				exec(entry[5])
			except Exception, e:
				self.session.open(MessageBox,("Code " + _("Error") + ": %s" % (e)),  MessageBox.TYPE_ERROR)

def quickSelectGlobal(self, key):
#	print "[Multi QuickButton] key: ", key
	if key:
		path = '/etc/MultiQuickButton/quickbutton_' + key + '.xml'
		if os.path.exists(path):
			self.checkQuickSel(path)
		else:
			self.session.open(MessageBox,("file %s not found!" % (path)),  MessageBox.TYPE_ERROR)

class MQBActionMap(ActionMap):
	def action(self, contexts, action):
		quickSelection = ('red','green','yellow','blue','vformat','picasa','shoutcast','youtube','find','f1','f2','f3','f4','sleep','spark','sat','fav','info','epg','file','playmode','usb','tvradio','tvsat','recall')
		if (action in quickSelection and self.actions.has_key(action)):
			res = self.actions[action](action)
			if res is not None:
				return res
			return 1
		else:
			return ActionMap.action(self, contexts, action)

def main(session,**kwargs):
	session.open(MultiQuickButton)

def menu(menuid, **kwargs):
	if menuid == "plugin":
		return [(_("Multi Quickbutton"), main, "multi_quick", 55)]
	return []

def Plugins(**kwargs):
	if config.plugins.QuickButton.mainmenu.value:
		return [PluginDescriptor(
				where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART],
				fnc = autostart),
				PluginDescriptor(
				name="Multi Quickbutton",
				description="Multi Quickbutton for Keyboard and RC",
				where = PluginDescriptor.WHERE_PLUGINMENU,
				icon="multiquickbutton.png",
				fnc=main),
				PluginDescriptor(
				name="Multi Quickbutton",
				where = PluginDescriptor.WHERE_EXTENSIONSMENU,
				fnc=main),
				PluginDescriptor(
				name="Multi Quickbutton",
				description="Multi Quickbutton for Keyboard and RC",
				where = PluginDescriptor.WHERE_MENU,
				fnc=menu)]

	else:
		return [PluginDescriptor(
				where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART],
				fnc = autostart),
				PluginDescriptor(
				name="Multi Quickbutton",
				description="Multi Quickbutton for Keyboard and RC",
				where = PluginDescriptor.WHERE_PLUGINMENU,
				icon="multiquickbutton.png",
				fnc=main),
				PluginDescriptor(
				name="Multi Quickbutton",
				where = PluginDescriptor.WHERE_EXTENSIONSMENU,
				fnc=main)]
