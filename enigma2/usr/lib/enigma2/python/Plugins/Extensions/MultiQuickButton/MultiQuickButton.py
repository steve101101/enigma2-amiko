
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.PluginComponent import plugins
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigLocations, ConfigText
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.LocationBox import LocationBox
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop
from QuickButtonList import QuickButtonList, QuickButtonListEntry
from QuickButtonXML import QuickButtonXML
from enigma import getDesktop
from Tools.Directories import *
import xml.sax.xmlreader
import os.path

config.plugins.QuickButton = ConfigSubsection()
config.plugins.QuickButton.enable = ConfigYesNo(default = True)
config.plugins.QuickButton.mainmenu = ConfigYesNo(default = True)
config.plugins.QuickButton.last_backupdir = ConfigText(default=resolveFilename(SCOPE_SYSETC))
config.plugins.QuickButton.backupdirs = ConfigLocations(default=[resolveFilename(SCOPE_SYSETC)])
MultiQuickButton_version = "2.4"
autostart=_("Autostart") + ": "
menuentry=_("Main menu") + ": "

class MultiQuickButton(Screen):

	global HD_Res

	try:
		sz_w = getDesktop(0).size().width()
	except:
		sz_w = 720

	if sz_w == 1280:
		HD_Res = True
	else:
		HD_Res = False

	if HD_Res:
		skin = """
		<screen position="240,100" size="800,520" title="Multi QuickButton Panel %s" >
			<widget name="list" position="10,10" size="780,450" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="2" position="20,490" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="2" position="210,490" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_yellow.png" zPosition="2" position="420,490" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_blue.png" zPosition="2" position="610,490" size="20,20" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="50,480" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="240,480" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="450,480" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="640,480" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,480" size="800,40" font="Regular;20" halign="left" valign="center" />
		</screen>""" % (MultiQuickButton_version)
	else:
		skin = """
		<screen position="50,90" size="620,420" title="Multi QuickButton Panel %s" >
			<widget name="list" position="10,10" size="600,350" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="2" position="10,390" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="2" position="160,390" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_yellow.png" zPosition="2" position="330,390" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_blue.png" zPosition="2" position="490,390" size="20,20" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="30,380" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="180,380" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="350,380" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="510,380" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,380" size="620,40" font="Regular;20" halign="left" valign="center" />
		</screen>""" % (MultiQuickButton_version)

	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.menu = args
		self.settigspath = ""
		self["background"] = Label('')
		self["key_red"] = Label(autostart)
		self["key_green"] = Label(menuentry)
		self["key_yellow"] = Label(_("Restore"))
		self["key_blue"] = Label(_("Backup"))
		list = []
		list.append(QuickButtonListEntry('1',('red', 'red')))
		list.append(QuickButtonListEntry('2',(_('green'),'green')))
		list.append(QuickButtonListEntry('3',(_('yellow'),'yellow')))
		list.append(QuickButtonListEntry('4',(_('blue'),'blue')))
		list.append(QuickButtonListEntry('5',('V.FORMAT','vformat')))
		list.append(QuickButtonListEntry('6',('PICASA','picasa')))
		list.append(QuickButtonListEntry('7',('SHOUTCAST','shoutcast')))
		list.append(QuickButtonListEntry('8',('YOUTUBE','youtube')))
		list.append(QuickButtonListEntry('9',(_('FIND'),'find')))
		list.append(QuickButtonListEntry('0',(_('F1'),'f1')))
		list.append(QuickButtonListEntry('',(_('F2'),'f2')))
		list.append(QuickButtonListEntry('',(_('F3'),'f3')))
		list.append(QuickButtonListEntry('',(_('F4'), 'f4')))
		list.append(QuickButtonListEntry('',(_('SLEEP'), 'sleep')))
		list.append(QuickButtonListEntry('',(_('SPARK'),'spark')))
		list.append(QuickButtonListEntry('',(_('TV/RADIO'),'tvradio')))
		list.append(QuickButtonListEntry('',(_('SAT'),'sat')))
		list.append(QuickButtonListEntry('',(_('FAV'),'fav')))
		list.append(QuickButtonListEntry('',(_('INFO'),'info')))
		list.append(QuickButtonListEntry('',(_('EPG'),'epg')))
		list.append(QuickButtonListEntry('',(_('FILELIST'),'file')))
		list.append(QuickButtonListEntry('',(_('PLAYMODE'),'playmode')))
		list.append(QuickButtonListEntry('',(_('USB'),'usb')))
		list.append(QuickButtonListEntry('',(_('RECALL'),'recall')))
		list.append(QuickButtonListEntry('',(_('TV/SAT'),'tvsat')))
		list.append(QuickButtonListEntry('',('about Multi Quickbutton rel. %s' % (MultiQuickButton_version), 'about')))

		self["list"] = QuickButtonList(list=list, selection = 0)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.run,
			"cancel": self.close,
			"red": self.autostart,
			"green": self.setMainMenu,
			"yellow": self.restore,
			"blue": self.backup
		}, -1)
		self.onShown.append(self.updateSettings)

	def updateSettings(self):
		autostart_state = autostart
		menuentry_state = menuentry
#		print "[MultiQuickButton].updateSettings enable: ",config.plugins.QuickButton.enable.getValue()
		if config.plugins.QuickButton.enable.value:
			autostart_state += _("on")
		else:
			autostart_state += _("off")

		if config.plugins.QuickButton.mainmenu.value:
			menuentry_state += _("on")
		else:
			menuentry_state += _("off")

		self["key_red"].setText(autostart_state)
		self["key_green"].setText(menuentry_state)

	def run(self):
		returnValue = self["list"].l.getCurrentSelection()[0][1]
		values = ('red','green','yellow','blue','vformat','picasa','shoutcast','youtube','find','f1','f2','f3','f4','sleep','spark','sat','fav','info','epg','file','playmode','usb','tvradio','tvsat','recall')
        	if returnValue is not None:
			if returnValue == 'about':
				self.session.open(MessageBox,("Multi Quickbutton idea is based on\nGP2\'s Quickbutton\nversion: %s\nby Emanuel CLI-Team 2009\nwww.cablelinux.info\n ***special thanks*** to:\ngutemine & AliAbdul & Dr.Best ;-)" % (MultiQuickButton_version)),  MessageBox.TYPE_INFO)

			elif returnValue in values:
				path = '/etc/MultiQuickButton/quickbutton_' + returnValue + '.xml'
				if os.path.exists(path) is True:
					self.session.open(QuickButton, path, ('Quickbutton: Key ' + _(returnValue)))
				else:
					self.session.open(MessageBox,("file %s not found!" % (path)),  MessageBox.TYPE_ERROR)

	def backup(self):
		self.session.openWithCallback(
			self.callBackup,
			BackupLocationBox,
			_("Please select the backup path..."),
			"",
			config.plugins.QuickButton.last_backupdir.value
		)
		
	def callBackup(self, path):
		if path is not None:
			if pathExists(path):
				config.plugins.QuickButton.last_backupdir.value = path
				config.plugins.QuickButton.last_backupdir.save()
				self.settigspath = path + "MultiQuickButton_settings.tar.gz"
				if fileExists(self.settigspath):
					self.session.openWithCallback(self.callOverwriteBackup, MessageBox,_("Overwrite existing Backup?."),type = MessageBox.TYPE_YESNO,)
				else:
					com = "tar czvf %s /etc/MultiQuickButton/" % (self.settigspath)
					self.session.open(Console,_("Backup Settings..."),[com])
			else:
				self.session.open(
					MessageBox,
					_("Directory %s nonexistent.") % (path),
					type = MessageBox.TYPE_ERROR,
					timeout = 5
					)
		else:
			print "[MultiQuickButton] backup cancel"

	def callOverwriteBackup(self, res):
		if res:
			com = "tar czvf %s /etc/MultiQuickButton/" % (self.settigspath)
			self.session.open(Console,_("Backup Settings..."),[com])

	def restore(self):
		self.session.openWithCallback(
			self.callRestore,
			BackupLocationBox,
			_("Please select the restore path..."),
			"",
			config.plugins.QuickButton.last_backupdir.value
		)

	def callRestore(self, path):
		if path is not None:
			self.settigspath = path + "MultiQuickButton_settings.tar.gz"
			if fileExists(self.settigspath):
				self.session.openWithCallback(self.callOverwriteSettings, MessageBox,_("Overwrite existing Settings?."),type = MessageBox.TYPE_YESNO,)
			else:
				self.session.open(MessageBox,_("File %s nonexistent.") % (path),type = MessageBox.TYPE_ERROR,timeout = 5)
		else:
			print "[MultiQuickButton] backup cancel"
			
	def callOverwriteSettings(self, res):
		if res:
			com = "cd /; tar xzvf %s" % (self.settigspath)
			self.session.open(Console,_("Restore Settings..."),[com])
		
	def autostart(self):
		if config.plugins.QuickButton.enable.value:
			config.plugins.QuickButton.enable.setValue(False)
			config.plugins.QuickButton.mainmenu.setValue(False)
		else:
			config.plugins.QuickButton.enable.setValue(True)

		print "[MultiQuickButton] enable: ",config.plugins.QuickButton.enable.getValue()
		self.updateSettings()
		config.plugins.QuickButton.enable.save()
		self.session.openWithCallback(self.callRestart,MessageBox,"Restarting Enigma2 to set\nMulti QuickButton Autostart", MessageBox.TYPE_YESNO, timeout=10)

	def setMainMenu(self):
		if config.plugins.QuickButton.mainmenu.value:
			config.plugins.QuickButton.mainmenu.setValue(False)
		else:
			config.plugins.QuickButton.mainmenu.setValue(True)

		config.plugins.QuickButton.mainmenu.save()
		self.updateSettings()
		self.session.openWithCallback(self.callRestart,MessageBox,"Restarting Enigma2 to load:\n" + _("Main menu") + "Multi QuickButton settings", MessageBox.TYPE_YESNO, timeout=10)

	def callRestart(self, restart):
		if restart == True:
			self.session.open(TryQuitMainloop, 3)
		else:
			pass


class BackupLocationBox(LocationBox):
	def __init__(self, session, text, filename, dir, minFree = None):
		inhibitDirs = ["/bin", "/boot", "/dev", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
		LocationBox.__init__(self, session, text = text, filename = filename, currDir = dir, bookmarks = config.plugins.QuickButton.backupdirs, autoAdd = True, editDir = True, inhibitDirs = inhibitDirs, minFree = minFree)
		self.skinName = "LocationBox"

class QuickButton(Screen):

	global HD_Res

	try:
		sz_w = getDesktop(0).size().width()
	except:
		sz_w = 720
		
	if sz_w == 1280:
		HD_Res = True
	else:
		HD_Res = False

	if HD_Res:
		skin = """
		<screen position="240,100" size="800,520" title="QuickButton" >
			<widget name="list" position="10,10" size="780,450" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="2" position="20,490" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="2" position="210,490" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_yellow.png" zPosition="2" position="400,490" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_blue.png" zPosition="2" position="590,490" size="20,20" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="50,480" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="240,480" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="430,480" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="620,480" zPosition="2"  size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,480" size="800,40" font="Regular;20" halign="left" valign="center" />
		</screen>"""
	else:
		skin = """
		<screen position="60,90" size="600,420" title="QuickButton" >
			<widget name="list" position="10,10" size="580,350" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="2" position="20,390" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="2" position="160,390" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_yellow.png" zPosition="2" position="300,390" size="20,20" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/button_blue.png" zPosition="2" position="440,390" size="20,20" alphatest="on" />
			<widget name="key_red" backgroundColor="#1f771f" zPosition="2" position="40,380" size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_green" backgroundColor="#1f771f" position="180,380" zPosition="2" size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_yellow" backgroundColor="#1f771f" position="320,380" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="key_blue" backgroundColor="#1f771f" position="460,380" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />
			<widget name="background" backgroundColor="#220a0a0a" zPosition="1" position="0,380" size="600,40" font="Regular;20" halign="left" valign="center" />
		</screen>"""

	def __init__(self, session, path=None, title = "" ):
		Screen.__init__(self, session)
		self.session = session
		self.path = path
		self.newtitle = title
		self.changed = False
		self.e = None
		list = []
		try:
			menu = xml.dom.minidom.parse(self.path)
			self.XML_db = QuickButtonXML(menu)
			for e in self.XML_db.getMenu():
				if e[1] == "1":
					list.append(QuickButtonListEntry('green',(e[0], '1')))
				else:
					list.append(QuickButtonListEntry('red',(e[0], '')))
		except Exception, e:
			self.e = e
			list = []
		
		self["list"] = QuickButtonList(list=list, selection = 0)
		self["background"] = Label('')
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		self["key_yellow"] = Label(_("delete"))
		self["key_blue"] = Label(_("Add"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], 
		{
			"ok": self.run,
			"cancel": self.cancel,
			"red": self.close,
			"green": self.save,
			"yellow": self.delete,
			"blue": self.add,
			"up": self.up,
			"down": self.down,
			"left": self.keyLeft,
			"right": self.keyRight
		}, -1)
		self.onExecBegin.append(self.error)
		self.onShown.append(self.updateTitle)

	def error(self):
		if self.e:
			self.session.open(MessageBox,("XML " + _("Error") + ": %s" % self.e),  MessageBox.TYPE_ERROR)
			print "[MultiQuickButton] XML ERROR: ",self.e
			self.close(None)

			
	def updateTitle(self):
		self.setTitle(self.newtitle)

	def run(self):
		returnValue = self["list"].l.getCurrentSelection()[0][1]
		name = self["list"].l.getCurrentSelection()[0][0]
		self.changed = True
        	if returnValue is not None:
			idx = 0;
			if returnValue is "1":
				list = []
				self.XML_db.setSelection(name, "")
				for e in self.XML_db.getMenu():
					if e[1] == "1":
						list.append(QuickButtonListEntry('green',(e[0], '1')))
						idx += 1
					else:
						list.append(QuickButtonListEntry('red',(e[0], '')))

			else:
				list = []
				self.XML_db.setSelection(name, "1")
				for e in self.XML_db.getMenu():
					if e[1] == "1":
						list.append(QuickButtonListEntry('green',(e[0], '1')))
						idx += 1
					else:
						list.append(QuickButtonListEntry('red',(e[0], '')))

			self["list"].setList(list)

	def save(self):
		self.XML_db.saveMenu(self.path)
		#self.close(None)
		self.changed = False
		self.cancel()

	def keyLeft(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.pageUp)
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def keyRight(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.pageDown)
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	def up(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveUp)
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def down(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveDown)
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	def getPluginsList(self):
		unic = []
		twins = [""]
		pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU ,PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO])
		pluginlist.sort(key = lambda p: p.name)
		for plugin in pluginlist:
			if plugin.name in twins:
				pass 
			else:
				unic.append((plugin.name, ""))
				twins.append(plugin.name)

		return unic

	def add(self):
		self.changed = True
		self.session.openWithCallback(self.QuickPluginSelected,ChoiceBox,"Plugins" ,self.getPluginsList())

	def QuickPluginSelected(self, choice):
		if choice:
			for entry in self["list"].list:
				if entry[0][0] == choice[0]:
#					print "[MultiquickButton] found blacksheep in QuickPluginSelected.list\n", entry[0][0]
					self.session.open(MessageBox,_("Entry %s already exists.") % (entry[0][0]),type = MessageBox.TYPE_ERROR,timeout = 5)
					return
				
			self.XML_db.addPluginEntry(choice[0])
			list = []
			for newEntry in self.XML_db.getMenu():
				if newEntry[1] == "1":
					list.append(QuickButtonListEntry('green',(newEntry[0], '1')))
				else:
					list.append(QuickButtonListEntry('red',(newEntry[0], '')))
					
			self["list"].setList(list)
			if len(self["list"].list) > 0:
				while 1:
					self["list"].instance.moveSelection(self["list"].instance.moveDown)
					if self["list"].l.getCurrentSelection()[0][0] != '--' or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
						break

	def delete(self):
		self.changed = True
		name = self["list"].l.getCurrentSelection()[0][0]
        	if name and name <> "--":
			print "[MultiquickButton] delete: ", name
			self.XML_db.rmEntry(name)

			list = []
			for e in self.XML_db.getMenu():
				if e[1] == "1":
					list.append(QuickButtonListEntry('green',(e[0], '1')))
				else:
					list.append(QuickButtonListEntry('red',(e[0], '')))

			lastValue="--"
			tmplist = []
			for i in list:
				if i[0][0] == "--" and lastValue == "--":
					lastValue = ""
				else:
					tmplist.append(i)
					lastValue = i[0][0]

			list = tmplist

			self["list"].setList(list)
			while 1:
					self["list"].instance.moveSelection(self["list"].instance.moveDown)
					if self["list"].l.getCurrentSelection()[0][0] != '--' or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
						break
	def cancel(self):
		if self.changed is True:
			self.session.openWithCallback(self.callForSaveValue,MessageBox,"Save Settings", MessageBox.TYPE_YESNO)
		else:
			self.close(None)

	def callForSaveValue(self, result):
		if result is True:
			self.save()
			self.close(None)
		else:
			self.close(None)