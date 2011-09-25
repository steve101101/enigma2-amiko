from Plugins.Plugin import PluginDescriptor
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.ActionMap import HelpableActionMap, NumberActionMap
from Screens.Screen import Screen
from Components.Sources.List import List
from enigma import eSize, ePoint, eTimer, loadPNG, quitMainloop, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, eListbox, gFont, getDesktop, ePicLoad, eServiceCenter, eServiceReference,iSeekableService,iServiceInformation, iPlayableService, iPlayableServicePtr
from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap
from Components.Label import Label   
from Components.Slider import Slider
from KTV_API import Kartina_Api
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Screens.InfoBarGenerics import InfoBarShowHide, NumberZap, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport
from datetime import datetime, date, timedelta
from Components.config import config, ConfigSubsection, ConfigYesNo, getConfigListEntry, ConfigInteger, ConfigText, ConfigSelection, ConfigSequence
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from time import time
from STATS import Stats_Api
from Screens.Standby import Standby
from Screens.InputBox import InputBox
from Components.Input import Input
from streams import iptv_streams
import hashlib
from __init__ import _
from enigma import eAVSwitch
from operator import itemgetter
from Components.AVSwitch import AVSwitch
from twisted.web.client import downloadPage
from VirtualKeyBoardRUS import VirtualKeyBoardRUS

try:
	import servicewebts
except Exception, ex: 
	print ex

global PLUGIN_PATH 
global PORNOPASS
PLUGIN_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/nKTVplayer'
PORNOPASS = 1414 

from enigma import addFont
try:
        addFont("%s/MyriadPro-Regular.otf" % PLUGIN_PATH, "RegularIPTV", 100, 1)
except Exception, ex: 
        print ex


config.plugins.ktv = ConfigSubsection()
config.plugins.ktv.login = ConfigInteger(147, (1, 99999999))
config.plugins.ktv.password = ConfigInteger(741, (1, 99999999))
config.plugins.ktv.time_show_now = ConfigInteger(5, (1, 10))
config.plugins.ktv.servicewebts = ConfigYesNo(default=True)
config.plugins.ktv.favorites = ConfigText(default='[]')
config.plugins.ktv.last_chid = ConfigText(default='2')
config.plugins.ktv.start_mode = ConfigSelection(default = "0", choices = [("0", _("KartinaTV FULL")), ("1", _("Videothek only")), ("2", _("Playlist only"))])
config.plugins.ktv.panscan = ConfigYesNo(default=False)

global PANSCANon4x3
PANSCANon4x3 = config.plugins.ktv.panscan.value
print PANSCANon4x3

favoriteList = eval(config.plugins.ktv.favorites.value)
global PLUGINMODE
PLUGINMODE = eval(config.plugins.ktv.start_mode.value)

def menu(menuid, **kwargs):
	plugin_name = ""
	if PLUGINMODE == 0:
		plugin_name = "KartinaTV"
	if PLUGINMODE == 1: 
		plugin_name = "KartinaTV Videothek"
	if PLUGINMODE == 2:
		plugin_name = "nStreamPlayer"
	if menuid == "mainmenu":
		return [(plugin_name, Ktv_api_start, "nktv_player", 9)]
	return []

		
def Ktv_api_start(session, **kwargs): 
	global KTV_API
	global STREAM_ID
	global STATE_API
	
	if config.plugins.ktv.servicewebts.value:
		STREAM_ID = 4112
	else:
		STREAM_ID = 4097    
	KTV_API = Kartina_Api(config.plugins.ktv.login.value, config.plugins.ktv.password.value)
	KTV_API.time_show_now = config.plugins.ktv.time_show_now.value
	KTV_API.favorite_list = favoriteList
	m = hashlib.md5()
	m.update("%i" % config.plugins.ktv.login.value)
	user_login_md5 = m.hexdigest() 
	STATE_API = Stats_Api(user_login_md5)

	if PLUGINMODE == 0:
		session.open(nKTVPlayer)
	if PLUGINMODE == 1: 
		session.open(VideothekPlaylist)
	if PLUGINMODE == 2:
		session.open(IPTVplayer)

class SelectFilmEpisode(Screen):

	skin = """	
		<screen name ="SelectFilmEpisode" position="center,center" size="412,300" backgroundColor="#41000000"  flags="wfNoBorder" title ="Episode selector" >
			<widget name="menulabel" position="40,30" zPosition="1" size="332,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" /> 
			<widget name="filmparts" itemHeight="30" position="40,80" size="332,250" backgroundColor="#41000000" foregroundColor="#ffffff" /> 
		</screen>"""

	def __init__(self, session, film_episodes = None):
		Screen.__init__(self, session)

		self.film_episodes = []
		self["actions"] = HelpableActionMap(self, "nKTV",
		{   
			"back": self.exit,
			"ok": self.ok,					
		}, -1)

		for x in range(len(film_episodes)):
			if not film_episodes[x][1]:
				text = 'EPISODE'
			else:
				text = film_episodes[1]
			self.film_episodes.append('%i. %s' % (x+1, text)) 

		self["filmparts"]=MenuList(self.film_episodes)
		self["menulabel"]=Label("SELECT THE EPISODE")

	def ok(self):  
		self.close(self["filmparts"].l.getCurrentSelectionIndex(), self.film_episodes)

	def exit(self):  
		self.close(None)		

class VideothekPlayer(Screen, InfoBarBase, InfoBarShowHide, InfoBarSeek):

	skin = """<screen name="VODplayer" position="0,550" size="1280,190" backgroundColor="#41000000" flags="wfNoBorder" title="Videothek">
		<ePixmap position="62,11" size="88,57" pixmap="%(path)s/img/player.png" zPosition="1" transparent="0" />
		<widget name="state" font="RegularIPTV;18" position="67,31" size="80,24" transparent="1" backgroundColor="#41000000" foregroundColor="#ffffff" zPosition="10" />

		<widget source="session.CurrentService" foregroundColor="#fa3d3d" render="Label" position="190,8"  size="90,20" font="RegularIPTV;18" halign="left" valign="center" backgroundColor="#06224f" transparent="1">
			<convert type="ServicePosition">Position</convert>
		</widget>
		<ePixmap  pixmap="%(path)s/img/slider_1280x10_hbg.png" position="190,35" size="900,10" zPosition="1" />
		<widget source="session.CurrentService" render="PositionGauge" backgroundColor="#206df9" position="190,35" size="900,10" zPosition="2" pointer="%(path)s/img/slider_1280x10_hfg.png:1290,0" transparent="1">
			<convert type="ServicePosition">Gauge</convert>
		</widget>
		<widget source="session.CurrentService" foregroundColor="#ffffff" render="Label" position="190,50" size="800,70" font="RegularIPTV;30" backgroundColor="#41000000" transparent="1">
			<convert type="ServiceName">Name</convert>
		</widget>
		<widget source="session.CurrentService" foregroundColor="#ffffff" render="Label" position="990,50" size="100,30" font="RegularIPTV;30" halign="right" backgroundColor="#41000000" transparent="1">
			<convert type="ServicePosition">Length</convert>
		</widget>
		<widget source="session.CurrentService" foregroundColor="#206df9" render="Label" position="1000,8" size="90,20" zPosition="2" font="RegularIPTV;20" halign="right" valign="center" backgroundColor="#41000000" transparent="1">
			<convert type="ServicePosition">Remaining</convert>
		</widget>
		<!-- <ePixmap position="1160,40" size="75,91" pixmap="%(path)s/img/kino.png"    zPosition="3" transparent="1" alphatest="blend" /> -->

		<!-- HELP GRAPHS -->
		<ePixmap position="190,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="193,128" size="32,24" pixmap="%(path)s/img/play.png"  zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="227,128" size="32,24" pixmap="%(path)s/img/pause.png"  zPosition="3" transparent="1" alphatest="blend" />		
		<eLabel position="261,132" zPosition="4" size="118,20" halign="center" font="RegularIPTV;18" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Play / Pause" /> 		

		<ePixmap position="426,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="429,128" size="32,24" pixmap="%(path)s/img/ff.png"   zPosition="3" transparent="1" alphatest="blend" /> 
		<eLabel position="463,132" zPosition="4" size="152,20" halign="center" font="RegularIPTV;18" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="FForward x2/x4/x8" /> 		

		<ePixmap position="660,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="663,128" size="25,24" pixmap="%(path)s/img/1.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="690,134" zPosition="4" size="32,16" halign="center" font="RegularIPTV;14" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="-10s" /> 		

		<ePixmap position="727,128" size="25,24" pixmap="%(path)s/img/4.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="753,134" zPosition="4" size="32,16" halign="center" font="RegularIPTV;14" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="-1m" /> 		

		<ePixmap position="790,128" size="25,24" pixmap="%(path)s/img/7.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="817,134" zPosition="4" size="32,16" halign="center" font="RegularIPTV;14" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="-5m" /> 		

		<ePixmap position="898,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />		
		<ePixmap position="901,128" size="25,24" pixmap="%(path)s/img/3.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="928,134" zPosition="4" size="32,16" halign="center" font="RegularIPTV;14" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="+10s" /> 		

		<ePixmap position="965,128" size="25,24" pixmap="%(path)s/img/6.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="991,134" zPosition="4" size="32,16" halign="center" font="RegularIPTV;14" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="+1m" /> 		

		<ePixmap position="1026,128" size="25,24" pixmap="%(path)s/img/9.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="1053,134" zPosition="4" size="32,16" halign="center" font="RegularIPTV;14" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="+5m" /> 		


		</screen>""" % {'path' : PLUGIN_PATH} 


 	def __init__(self, session, vod_entry = None):
		Screen.__init__(self, session)

		InfoBarBase.__init__(self, steal_current_service=True)
		InfoBarShowHide.__init__(self)
		InfoBarSeek.__init__(self, actionmap = "InfobarSeekActions")
		self.InfoBar_NabDialog = Label()
		self.session = session		

		self.service = None
		self["state"] =  Label(' WAIT')

		self.StateTimer = eTimer()
		self.onShown.append(self.setState)
		self.StateTimer.callback.append(self.setState)
		
		self.vod_entry = vod_entry
		self.film_episodes = self.vod_entry[9]
		first_film = self.film_episodes[0][0]
		self.vod_url = KTV_API.vod_geturl(first_film)
		self.title = self.vod_entry[0]
		if self.vod_entry[1]:
			self.title = self.title + '\n%s' % self.vod_entry[1]		

		if self.vod_url is not None:
			self.session.nav.stopService()
			self.reference = eServiceReference(4097,0,self.vod_url)
			self.reference.setName(self.title)

		self["actions"] = HelpableActionMap(self, "nKTV",
		{   
			"back": self.exit,
			"ok": self.toggleShow #cube fix 
		}, -1) 


		if len(self.film_episodes)>1:
			self.onFirstExecBegin.append(self.part_selector)
		else:
			self.onFirstExecBegin.append(self.play_vod)

		self.onPlayStateChanged.append(self.__playStateChanged)
	
	#cube fix
	def openEventView(self): 
		self.fix = ""

	def cbSelectPart(self, episode = None, film_episodes = None):
		if episode >-1:
			self.vod_url = KTV_API.vod_geturl(self.film_episodes[episode][0])
			self.reference = eServiceReference(4097,0,self.vod_url)
			self.reference.setName(self.title+' / %s' % film_episodes[episode])
			self.play_vod()
		else:
			self.exit()

	def __playStateChanged(self, state):       
		print self.seekstate[3]
		text = ' ' + self.seekstate[3]
		if self.seekstate[3]=='>':
			text = ' PLAY     >'
		if self.seekstate[3]=='||':
			text = 'PAUSE   ||'			
		if self.seekstate[3]=='>> 2x':
			text = '    x2     >>'
		if self.seekstate[3]=='>> 4x':
			text = '    x4     >>' 
		if self.seekstate[3]=='>> 8x':
			text = '    x8     >>'

		self["state"].setText(text)

		if self.seekstate[3]=='END':
			#self.toggleShow()
			#self.doSeekRelative(0)
			self.pauseService()
			self.unPauseService()

	def setState(self):
		STATE_API.set_state_vod(self.vod_entry[10])
		self.StateTimer.start(5000, True)
		
	def part_selector(self):
		self.session.openWithCallback(self.cbSelectPart, SelectFilmEpisode, film_episodes = self.film_episodes)

	def play_vod(self):
		if self.reference:
			try:    
				self.session.nav.playService(self.reference)
			except:
				print 'vod play error'

	def exit(self):  
		self.close()
		
		
def videothekPlaylistEntry(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_TEXT,7,10,32,33,1,RT_HALIGN_CENTER,'%s' % entry[12]),
	(eListboxPythonMultiContent.TYPE_TEXT,50,7,640,22,1,RT_HALIGN_LEFT,entry[2]),
	(eListboxPythonMultiContent.TYPE_TEXT,680,7,40,22,1,RT_HALIGN_LEFT,entry[6]),  
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 50, 30, 670, 2, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH))
	]

	return menu_entry

def videothekGenlistEntry(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_TEXT,5,5,360,37,0,RT_HALIGN_LEFT,entry[1]),
	] 
	return menu_entry

class VideothekPlaylist(Screen):
	skin = """	
	<screen name ="MyChannelSelection" position="0,0" size="1280,720" backgroundColor="#41000000" flags="wfNoBorder" > 

		<widget name="feedlist" position="50,50" size="760,592" foregroundColorSelected="#ffffff" backgroundColor="#41000000" foregroundColor="#76addc" backgroundColorSelected="#41000000" selectionPixmap="%(path)s/img/x37.png"  enableWrapAround="1" zPosition="1" scrollbarMode="showOnDemand" transparent="0" />   

		<widget name="film_info" position="50,50" size="760,592" backgroundColor="#41000000" foregroundColor="#ffffff" font="RegularIPTV;22" zPosition="10" transparent="0" />   

		<widget name="ramka1" position="50,610" size="126,30" pixmap="%(path)s/img/rahmen126x30.png" backgroundColor="#41000000" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="chminus" position="53,613" size="32,24" pixmap="%(path)s/img/chminus.png" zPosition="2" transparent="1" alphatest="blend" />
		<widget name="chprev"  position="86,618" zPosition="3" size="86,19" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="PREVIEW" />   	
		<widget name="ramka2" position="658,610" size="126,30" pixmap="%(path)s/img/rahmen126x30.png" backgroundColor="#ffffff" zPosition="1" transparent="1" alphatest="blend" />  
		<widget name="chplus"  position="749,613" size="32,24" pixmap="%(path)s/img/chplus.png" zPosition="2" transparent="1" alphatest="blend" />
		<widget name="chnext"  position="662,618" zPosition="3" size="86,19" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="NEXT" />

		<widget name="site_list"  position="177,611" zPosition="3" size="480,28" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;26" text="" /> 

		<widget name="grouplist" foregroundColorSelected="#ffffff" backgroundColor="#41000000" foregroundColor="#76addc" backgroundColorSelected="#41000000" selectionPixmap="%(path)s/img/x37small.png" scrollbarMode="showOnDemand" position="826,50" size="380,552" zPosition="1"  /> 
		<widget backgroundColor="#41000000" foregroundColor="#ffffff" position="826,55" size="390,440" name="description" font="RegularIPTV;22" />
		<widget name="poster" position="1000,520" size="120,171" pixmap="%(path)s/img/test.png" zPosition="1" transparent="1" alphatest="blend" />

		<widget name="rat1s" position="840,580" size="120,24" pixmap="%(path)s/img/stars.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="rat2s" position="840,630" size="120,24" pixmap="%(path)s/img/stars.png" zPosition="1" transparent="1" alphatest="blend" />

		<widget name="rat1" position="840,580" size="120,24" pixmap="%(path)s/img/stars_gold.png" zPosition="2" transparent="1" />
		<widget name="rat2" position="840,630" size="120,24" pixmap="%(path)s/img/stars_gold.png" zPosition="2" transparent="1" />

		<widget name="text_rat1" position="840,565" zPosition="1" size="120,24" halign="center" font="RegularIPTV;16" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="IMDB" />
		<widget name="text_rat2" position="840,615" zPosition="1" size="120,24" halign="center" font="RegularIPTV;16" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Kinopoisk" />

		<widget name="epg_ramka" position="837,520" size="126,30" pixmap="%(path)s/img/rahmen126x30.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="epg_img" position="840,523" size="32,24" pixmap="%(path)s/img/epg.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="epg_text"  position="872,528" zPosition="1" size="86,16" halign="center" font="RegularIPTV;16" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="MORE INFO" />

		<ePixmap position="47,668" size="92,30" pixmap="%(path)s/img/rahmen.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="50,671" size="32,24" pixmap="%(path)s/img/menu.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="button1" position="85,676" zPosition="1" size="50,24" halign="center" font="RegularIPTV;16" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="ALL Z-A" />

		<ePixmap position="0,700"  size="1280,11" pixmap="%(path)s/img/tab_line.png"     zPosition="1" transparent="1" alphatest="blend" />		
		<ePixmap position="147,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="351,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="555,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="759,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />

		<ePixmap position="1160,600" size="75,91" pixmap="%(path)s/img/kino.png"    zPosition="3" transparent="1" alphatest="blend" />
		<widget name = "country" halign="center" font="RegularIPTV;16" position="1160,520" size="75,80" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" zPosition="1" />
		<widget name = "total" halign="center" font="RegularIPTV;40" position="1160,650" size="75,40" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" zPosition="6" />

		<widget name="tab1" position="147,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<widget name="tab2" position="351,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<widget name="tab3" position="555,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<widget name="tab4" position="759,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<ePixmap position="155,671" size="25,25" pixmap="%(path)s/img/red.png"    zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="359,671" size="25,25" pixmap="%(path)s/img/green.png"  zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="563,671" size="25,25" pixmap="%(path)s/img/yellow.png" zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="767,671" size="25,25" pixmap="%(path)s/img/blue.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="187,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="BEST" />
		<eLabel position="391,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="LAST" />
		<eLabel position="593,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="GENRE" />
		<eLabel position="800,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="SEARCH" />	</screen>""" % {'path' : PLUGIN_PATH} 

	def __init__(self, session):
		Screen.__init__(self, session)   
		self.session = session     
		self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.mlist.l.setFont(1, gFont('RegularIPTV', 20)) 
		self.mlist.l.setFont(2, gFont('RegularIPTV', 12)) 
		self.mlist.l.setItemHeight(37)  
		self["feedlist"] = self.mlist
		self.InfoBar_NabDialog = Label('')


		self.film_list = KTV_API.get_vod_list('best','1','','','16')   
		self.mlist.setList(map(videothekPlaylistEntry, self.film_list))
		self.onShown.append(self.best)

		self.onFirstExecBegin.append(self.updateTitle)

		self.gen_list = KTV_API.get_genres()


		self.glist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.glist.l.setFont(0, gFont('RegularIPTV', 26))
		self.glist.l.setItemHeight(37)
		self['grouplist'] = self.glist
		self.glist.setList(map(videothekGenlistEntry, self.gen_list))
		self['grouplist'].hide()

		self.mlist.onSelectionChanged.append(self.updateTitle)
		self.glist.onSelectionChanged.append(self.updateCategory)

		self['tab1'] = Pixmap()
		self['tab2'] = Pixmap()
		self['tab3'] = Pixmap()
		self['tab4'] = Pixmap()
		self['tab1'].hide()
		self['tab2'].hide()
		self['tab3'].hide()
		self['tab4'].hide()
		self['rat1'] = Slider(0, 120)
		self['rat2'] = Slider(0, 120)
		#self['rat3'] = Slider(0, 120)
		self['description'] = Label()
		self['button1'] = Label()
		self['country'] = Label()
		self.mode = -1
		self.sort_mode = 1
		self.film_info = 0

		self['poster'] = Pixmap()
		self.picload = ePicLoad()
		self['text_rat1'] = Label()
		self['text_rat2'] = Label()
		#self['text_rat3'] = Label()
		self['rat1s'] = Pixmap()
		self['rat2s'] = Pixmap()
		#self['rat3s'] = Pixmap()		


		self['ramka1'] = Pixmap()
		self['chminus'] = Pixmap()
		self['chprev'] = Label()
		self['ramka2'] = Pixmap()
		self['chplus'] = Pixmap()
		self['chnext'] = Label()
		self['site_list'] = Label()
		self['film_info'] = Label()
		self['film_info'].hide()

		self['epg_img'] = Pixmap()
		self['epg_ramka'] = Pixmap()
		self['epg_text'] = Label()

		self.page = 1
		self.page_counter = 0

		self.PosterTimer = eTimer()
		self.PosterTimer.callback.append(self.decodeImage)
		self.vod_player_state = 0
		self['total'] = Label('%i' % KTV_API.total)

		self["actions"] = HelpableActionMap(self, "nKTV", 
		{
			"ok": self.ok,
			"back": self.exit_box,
			"red": self.best,
			"green": self.last,			
			"yellow": self.show_category,
			"blue": self.mySearch,
			"menu": self.sorting,
			"channelPlus": self.nextPage,
			"channelMinus": self.prevPage,
			"showEPGList": self.showFilminfo,
			"help": self.setup,
		}, -1)

	def setup(self):  	
		self.session.open(KtvSetup)
		
	def mySearch(self):
		self.session.openWithCallback(self.searchResult, VirtualKeyBoardRUS, title = (_("Enter your search term(s)")), text = "")

	def searchResult(self, message=None):
		if message:
			result = KTV_API.get_vod_list('text','1','%s' % message,'','500')
			if result:
				self.film_list = result
				self['tab1'].hide()
				self['tab2'].hide()
				self['tab3'].hide()
				self['tab4'].show()				
				self.mlist.moveToIndex(0)		    
				self.mlist.setList(map(videothekPlaylistEntry, result))
				self.mode = 3
				self.page_info_disabler()
			else:
				self.session.open(MessageBox, _('no result'), type=MessageBox.TYPE_INFO, timeout = 3)


	def showFilminfo(self):

		if self.film_info == 1:
			self['film_info'].hide()
			self.film_info = 0
			#self['epg_img'].instance.setPixmapFromFile('%s/img/epg.png' % PLUGIN_PATH)
			self['epg_text'].setText('MORE INFO')
			self.updateTitle()
		else:
			#self['epg_img'].instance.setPixmapFromFile('%s/img/exit.png' % PLUGIN_PATH)
			self['epg_text'].setText('CLOSE INFO')
			self.film_info = 1
			self['film_info'].show()
			index = self.mlist.getSelectionIndex()
			film_id = self.film_list[index][0]
			film_info = KTV_API.get_vod_info(film_id)
			parts = len(film_info[9])
			part_info = '' 
			if parts>1:
				part_info = 'EPISODE:'
				for x in range(parts):
					part_info = part_info + '\n%i %s' % (x+1, film_info[9][x][1])


			original_name = ''
			if film_info[1]:
				original_name = ' (%s)' % film_info[1]
			self['film_info'].setText('%s %s\n\n %s\n\n%s' % (film_info[0], original_name, film_info[2], part_info ))
			self['description'].setText('lenght: %s (min)\nyear: %s\ngenre: %s\ndirector: %s\nscenario: %s\nactors:\n %s' % (film_info[3], film_info[4], film_info[5], film_info[6], film_info[7], film_info[8]))


	def fill_vod(self):
		if len(KTV_API.all_vod_list)==0:
			self.film_list = KTV_API.get_vod_list('best','1','','','500','no counter')
			KTV_API.all_vod_list = self.film_list

	def sorting(self):
		self.fill_vod()
		self['tab1'].hide()
		self['tab2'].hide()
		self['tab3'].hide()
		self['tab4'].hide()
		self['grouplist'].hide()
		self.mlist.selectionEnabled(1)
		self.mlist.moveToIndex(0)
		if self.sort_mode == 0:
			self['button1'].setText('ALL Z-A')
			self.film_list = sorted(KTV_API.all_vod_list, key = itemgetter(2), reverse=False)
			self.sort_mode = 1
		else:
			self['button1'].setText('ALL A-Z')
			self.film_list = sorted(KTV_API.all_vod_list, key = itemgetter(2), reverse=True)
			self.sort_mode = 0
		self.mlist.setList(map(videothekPlaylistEntry, self.film_list))
		self.mode = 4
		self.updateTitle()


	def set_site_number(self):
		counter = KTV_API.total/KTV_API.nums 
		if KTV_API.total%KTV_API.nums>0:
			counter = counter + 1

		self.page_counter = counter
		page_from = KTV_API.page-5
		if page_from < 1:
			page_from = 1
		page_to = KTV_API.page+5
		if page_to > counter + 1:
			 page_to = counter + 1
		text = '-'
		for x in range(page_from,page_to):
			if x != KTV_API.page:
				text = text + '%i-' %x
			else:
				text = text + '[%i]-' % x
		self['site_list'].setText("%s (%i)" % (text,counter))

	def page_info_disabler(self):
		if self.mode == 0 or self.mode == 1:
			self['ramka1'].show()
			self['chminus'].show()
			self['chprev'].show()
			self['ramka2'].show()
			self['chplus'].show()
			self['chnext'].show()
			self['site_list'].show()
		else:
			self['ramka1'].hide()
			self['chminus'].hide()
			self['chprev'].hide()
			self['ramka2'].hide()
			self['chplus'].hide()
			self['chnext'].hide()
			self['site_list'].hide()
	def nextPage(self):  
		self.page +=1
		if self.page > self.page_counter:
			self.page = 1          
		self.set_mode() 

	def prevPage(self):
		self.page -=1
		if self.page == 0:
			self.page = self.page_counter	
		self.set_mode()

	def set_mode(self):
		if self.mode == 0:
			self.best()
		if self.mode == 1:
			self.last()

	def best(self):
		if self.mode != 0:
			self.page = 1		
		self.film_list = KTV_API.get_vod_list('best','%i' % self.page,'','','15')
		self.set_site_number()
		self.mlist.selectionEnabled(1)
		self.mlist.moveToIndex(0)		    
		self.mlist.setList(map(videothekPlaylistEntry, self.film_list))
		self['tab1'].show()
		self['tab2'].hide()
		self['tab3'].hide()
		self['tab4'].hide()
		self['grouplist'].hide()
		self.mode = 0
		self.updateTitle()

	def last(self):
		if self.mode != 1:
			self.page = 1
		self.film_list = KTV_API.get_vod_list('last','%i' % self.page,'','','15')
		self.set_site_number()
		self.mlist.selectionEnabled(1)
		self.mlist.moveToIndex(0)		     
		self.mlist.setList(map(videothekPlaylistEntry, self.film_list))
		self['tab1'].hide()
		self['tab2'].show()
		self['tab3'].hide()
		self['tab4'].hide()
		self.mode = 1
		self.updateTitle()

	def show_category(self):
		self.updateCategory()
		self['tab1'].hide()
		self['tab2'].hide()
		self['tab3'].show()
		self['tab4'].hide()
		self.mode = 2
		self.updateCategory()


	def film_info_disabler(self):
		self.page_info_disabler()
		if self.mode == 2:
			self['grouplist'].show()
			self['description'].hide()
			self['rat1'].hide()
			self['rat2'].hide()
			#self['rat3'].hide()
			self['rat1s'].hide()
			self['rat2s'].hide()
			#self['rat3s'].hide()		
			self['country'].hide()
			self['text_rat1'].hide()
			self['text_rat2'].hide()
			#self['text_rat3'].hide()
			self['poster'].hide()
			self['epg_ramka'].hide()
			self['epg_img'].hide()
			self['epg_text'].hide()
		else:
			self['grouplist'].hide()
			self['description'].show()
			self['rat1'].show()
			self['rat2'].show()
			#self['rat3'].show()
			self['rat1s'].show()
			self['rat2s'].show()
			#self['rat3s'].show()		
			self['country'].show()
			self['text_rat1'].show()
			self['text_rat2'].show()
			#self['text_rat3'].show()
			self['poster'].show()
			self['epg_ramka'].show()
			self['epg_img'].show()
			self['epg_text'].show()			

	def updateCategory(self):
		try:
			self.film_info_disabler() 		
			gr_id = self.gen_list[self.glist.getSelectionIndex()][0]
			self.film_list = KTV_API.get_vod_list('best','1','','%s' % gr_id,'500')       
			self.mlist.setList(map(videothekPlaylistEntry, self.film_list))
			self.mlist.selectionEnabled(0)
		except:
			print 'updateCategory error'

	def updateTitle(self):
		try:	
			self.film_info_disabler()
			index = self.mlist.getSelectionIndex()
			entry = self.film_list[index]
			downloadPage('http://iptv.kartina.tv%s' % entry[5],'/tmp/cover.jpg')
			self.picfile = "/tmp/cover.jpg"

			self['description'].setText(entry[4])
			self['country'].setText('Country:\n%s' % entry[10])

			self.decodeImage()
			self.PosterTimer.start(500, True)
			if self.film_info == 1:
				self.film_info = 0
				self.showFilminfo()
			if entry[7]:
				rat1 = entry[7]
			else:
				rat1 = 0 
			self['rat1'].setValue(int(12 * float(rat1)))

			if entry[8]:
				rat2 = entry[8]
			else:
				rat2 = 0 
			self['rat2'].setValue(int(12 * float(rat2)))
			#if int(entry[9]):
			#	rat3 = entry[9]
			#else:
			#	rat3 = 0 
			#self['rat3'].setValue(int(12 * float(rat3)))

		except:
			print 'updateTitle error'

	def decodeImage(self): 
		picture = self.picfile
		picload = self.picload
		sc = AVSwitch().getFramebufferScale() 
		picload.setPara((120, 171, sc[0], sc[1], 0, 0, '#ff000000')) 
		l = picload.PictureData.get()
		del l[:]
		l.append(self.showImage) 
		picload.startDecode(picture)

	def showImage(self, picInfo = None):
		ptr = self.picload.getData() 
		if ptr: 
			self["poster"].instance.setPixmap(ptr.__deref__())

	def ok(self):
		if self.mode == 2: 
			self.mlist.selectionEnabled(1)
			self['grouplist'].hide()
			self.mode = 20
			self.film_info_disabler()  
		elif self.mode != 2:   
			self.play()



	def play(self):
		entry = self.film_list[self.mlist.getSelectionIndex()][0]
		film_info = KTV_API.get_vod_info(entry)
		if entry: 
			self.session.open(VideothekPlayer, film_info)

   
	def exit(self):
		if self.mode == 20:
			self.show_category()
		if self.film_info == 1:
			self.showFilminfo()
		else: 
			self.exit_box()

	def exit_box(self):
		self.session.openWithCallback(self.exit_check, MessageBox, _("Exit Videothek?"), type=MessageBox.TYPE_YESNO)

	def exit_check(self, message=None):
		if message:
			self.close()			


   
class MyIptvPlaylist(Screen):
	skin = """	
	<screen name ="MyIptvPlaylist" position="0,0" size="1280,720" backgroundColor="#41000000" flags="wfNoBorder" title="IPTV Playlist" > 
		<widget name="feedlist" position="50,50" size="760,592" foregroundColorSelected="#ffffff" backgroundColor="#41000000" foregroundColor="#76addc" backgroundColorSelected="#41000000" selectionPixmap="%(path)s/img/x37.png"  enableWrapAround="1" zPosition="1" scrollbarMode="showOnDemand" transparent="0" />   
		<widget name="grouplist" foregroundColorSelected="#ffffff" backgroundColor="#41000000" foregroundColor="#76addc" backgroundColorSelected="#41000000" selectionPixmap="%(path)s/img/x37small.png" scrollbarMode="showOnDemand" position="826,92" size="380,552" zPosition="1"  />
		<ePixmap position="0,700"  size="1280,11" pixmap="%(path)s/img/tab_line.png"     zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="147,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="351,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />		
		<widget name="tab1" position="147,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<widget name="tab2" position="351,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<ePixmap position="155,671" size="25,25" pixmap="%(path)s/img/red.png"    zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="359,671" size="25,25" pixmap="%(path)s/img/green.png"  zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="187,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="All Channels" />
		<eLabel position="391,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Categories" />
		<widget name="time" position="1120,650" size="114,44" font="RegularIPTV;48" foregroundColor="#ffffff" backgroundColor="#000000" />
		<ePixmap position="1117,645" size="116,51" pixmap="%(path)s/img/flip_clock4.png" zPosition="3" transparent="1" alphatest="blend" />		
	</screen>""" % {'path' : PLUGIN_PATH} 

	def __init__(self, session, index = None):
		Screen.__init__(self, session)   
		self.session = session 
				 
		self.channel_list = STREAMS.iptv_list
		self.group_list	= STREAMS.groups
		if index:
			self.index = index
		else:
			self.index = 0
		self.mode = 0
		self["time"] = Label()
		self['tab1'] = Pixmap()
		self['tab2'] = Pixmap()		

		self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.mlist.l.setFont(0, gFont('RegularIPTV', 22))
		self.mlist.l.setFont(1, gFont('RegularIPTV', 20)) 
		self.mlist.l.setFont(2, gFont('RegularIPTV', 14)) 
		self.mlist.l.setFont(3, gFont('RegularIPTV', 12))
		self.mlist.l.setItemHeight(37)  
		self["feedlist"] = self.mlist
		self.mlist.setList(map(channelEntryIPTVplaylist, self.channel_list))


		self.glist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.glist.l.setFont(0, gFont('RegularIPTV', 24))
		self.glist.l.setItemHeight(37) 
		self['grouplist'] = self.glist
		self.glist.setList(map(groupEntryIPTVplaylist, self.group_list))
		self['grouplist'].hide()

		self.glist.onSelectionChanged.append(self.update_channellist)
		self.mlist.onSelectionChanged.append(self.update_category)
		self.onShown.append(self.show_all)

		self["actions"] = HelpableActionMap(self, "nKTV", 
		{
			"red": self.show_all,
			"green": self.show_category,
			"ok": self.ok,
			"back": self.exit,
			"help": self.setup,
		}, -1)

	def setup(self):  	
		self.session.open(KtvSetup)

	def show_category(self):
		self['tab1'].hide()
		self['tab2'].show()		
		self["time"].setText(datetime.fromtimestamp(time()).strftime('%H:%M'))
		self['grouplist'].show()	
		self.mlist.selectionEnabled(0)
		self.glist.selectionEnabled(1) 
		self.mlist.setList(map(channelEntryIPTVplaylist, self.group_list[0][3]))
		self.mlist.moveToIndex(0)
		self.mode = 2


	def update_channellist(self):
		print self.glist.getSelectionIndex()
		group_index = self.glist.getSelectionIndex()
		self.channel_list = self.group_list[group_index][3]
		self.mlist.setList(map(channelEntryIPTVplaylist, self.channel_list))


	def show_all(self):
		self['tab2'].hide()
		self['tab1'].show()		
		self["time"].setText(datetime.fromtimestamp(time()).strftime('%H:%M'))
		self.channel_list = STREAMS.iptv_list
		self['grouplist'].hide()
		self.mlist.setList(map(channelEntryIPTVplaylist, self.channel_list))
		self.mlist.moveToIndex(self.index)
		self.mlist.selectionEnabled(1)
		self.glist.selectionEnabled(0)
		self.mode = 0 
		
	def openEventView(self): 
		self.fix = ""

	def update_category(self):
		print 'update_category'

	def exit(self):
		if self.mode == 20:
			self.show_category()
		else:	
			self.close()

	def ok(self):
		if self.mode == 2:
			self['grouplist'].hide() 
			self.mlist.selectionEnabled(1)
			self.mlist.moveToIndex(0)
			self.mode = 20   
		elif self.mode != 2: 
			self.close(int(self.channel_list[self.mlist.getSelectionIndex()][0])-1)					



class IPTVplayer(Screen, InfoBarBase, InfoBarShowHide, InfoBarAudioSelection, InfoBarSubtitleSupport):

	skin = """
	<screen name ="IPTVPlayer" position="0,550" size="1280,190" backgroundColor="#41000000" flags="wfNoBorder" title="IPTV Player">
	    <ePixmap position="80,4" size="72,36" pixmap="%(path)s/img/72x36.png" zPosition="1" transparent="0" />
		<widget position="84,7" halign="center" size="64,28" foregroundColor="#ffffff" zPosition="2" name="channel_number" transparent="1" font="RegularIPTV;34"/>
		<widget position="160,7" size="650,34" foregroundColor="#ffffff" backgroundColor="#41000000" name="channel_name" font="RegularIPTV;34"/>
		<widget position="805,10" size="300,26" halign="right" foregroundColor="#f4df8d" backgroundColor="#41000000" name="group" font="RegularIPTV;26"/>
		<widget name="picon" position="120,68" size="35,35" backgroundColor="#41000000" />
		<ePixmap position="80,50" size="117,72" pixmap="%(path)s/img/pristavka.png" zPosition="10" transparent="1" alphatest="blend" />   	 
		<widget position="300,56" size="650,25" foregroundColor="#ffffff" backgroundColor="#41000000" name="programm" font="RegularIPTV;24"/>

		<ePixmap position="1115,4" size="72,36" pixmap="%(path)s/img/72x36.png" zPosition="1" transparent="0" /> 
		<widget  position="1118,9" size="66,26" foregroundColor="#ffffff" halign="center" zPosition="2" name="time_now" transparent="1" font="RegularIPTV;28"/>
		<ePixmap position="1070,50" size="117,72" pixmap="%(path)s/img/network.png" zPosition="1" transparent="1" alphatest="blend" />		
	</screen>""" % {'path' : PLUGIN_PATH}


 	def __init__(self, session):
		Screen.__init__(self, session)
		InfoBarBase.__init__(self, steal_current_service=True)
		InfoBarShowHide.__init__(self)
		InfoBarAudioSelection.__init__(self)
		InfoBarSubtitleSupport.__init__(self) 
		
		global STREAMS
		
		STREAMS = iptv_streams()
		try:
			STREAMS.readfile()
		except:
			'm3u eroor'
		STREAMS.get_list()
				
		self['channel_name'] = Label('')
		self['picon'] = Pixmap()
		self['programm'] = Label('')
		self.InfoBar_NabDialog = Label('')
		self.session = session
		self['channel_number'] = Label('')
		self.channel_list = STREAMS.iptv_list
		self.group_list	= STREAMS.groups
		self.index = 0
		self.group_index = 0
		self['group'] = Label('')
		self['time_now'] = Label('')
		self.mode = 0

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.onFirstExecBegin.append(self.play_channel)

		self["actions"] = HelpableActionMap(self, "nKTV",
		{
			"back": self.exit_box,
			"left": self.prevChannel,
			"right": self.nextChannel,
			"up": self.show_channel_list,
			"channelPlus": self.nextGroup,
			"channelMinus": self.prevGroup,
		}, -1)                                            

		self["myNumberActions"] = NumberActionMap(["NumberActions", "InfobarAudioSelectionActions", "InfobarTeletextActions"],
		{   
 			"1": self.keyNumberGlobal,
 			"2": self.keyNumberGlobal,
 			"3": self.keyNumberGlobal,
 			"4": self.keyNumberGlobal,
 			"5": self.keyNumberGlobal,
 			"6": self.keyNumberGlobal,
 			"7": self.keyNumberGlobal,
 			"8": self.keyNumberGlobal,
 			"9": self.keyNumberGlobal,
 			"0": self.keyNumberGlobal
		}, -1)

	def openEventView(self): 
		self.fix = ""
		
	def show_channel_list(self):
		self.session.openWithCallback(self.channel_answer, MyIptvPlaylist, self.index)

	def channel_answer(self, index = None): 
		if index > -1:
			self.index = index		
			self.play_channel()		

	def keyNumberGlobal(self, number):    
		self.session.openWithCallback(self.numberEntered, NumberZap, number)

	def numberEntered(self, num):
		self.index = num - 1
		if self.index >= 0:
			if self.index < len(self.channel_list):
				self.play_channel()			

	def play_channel(self):
		self['time_now'].setText(datetime.fromtimestamp(time()).strftime('%H:%M'))
		entry = self.channel_list[self.index]
		self['channel_number'].setText('%i' % entry[0])
		self['channel_name'].setText(entry[1])
		self['programm'].setText(entry[3])
		self['picon'].instance.setPixmapFromFile('%s/picon35x35/%s' % (PLUGIN_PATH,entry[2]))
		self['group'].setText("[%i] %s" % (entry[6], entry[7]))
		self.group_index = entry[6]-1

		if(entry[4]):
			id_s = 4112
		else:
			id_s = 4097
		url = entry[3]
		self.session.nav.stopService()
		sref = eServiceReference(id_s, 0, url)
		if entry[5]:
			sref.setData(2,int(entry[5])*1024)
		try:    
			self.session.nav.playService(sref)
		except:
			print 'play_channel error'

	def nextChannel(self):  
		self.index +=1
		if self.index == len(self.channel_list):
			self.index = 0          
		self.play_channel() 

	def prevChannel(self):
		self.index -=1
		if self.index == -1:
			self.index = len(self.channel_list)-1	
		self.play_channel()

	def nextGroup(self):
		if self.group_index < len(self.group_list)-1:
			self.group_index_temp = self.group_index + 1	 	
			self.index = (self.group_list[self.group_index_temp][3][0][0])-1
		else:
			self.group_index = 0
			self.index = 0
		self.play_channel()		

	def prevGroup(self):
		if self.group_index >= 1 :
			self.group_index_temp = self.group_index - 1
			self.index = (self.group_list[self.group_index_temp][3][0][0])-1
		else:
			last_group = len(self.group_list) - 1
			self.index = (self.group_list[last_group][3][0][0])-1
		self.play_channel()	

	def exit_box(self):
		self.session.openWithCallback(self.exit, MessageBox, _("Exit Playlist?"), type=MessageBox.TYPE_YESNO)

	def exit(self, message=None):
		if message:
			self.session.nav.playService(self.oldService)	
			self.close()

def groupEntryIPTVplaylist(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_TEXT,5,7,60,37,0,RT_HALIGN_LEFT,'%i' % entry[0]),
	(eListboxPythonMultiContent.TYPE_TEXT,40,7,255,37,0,RT_HALIGN_LEFT,entry[1]),  
	(eListboxPythonMultiContent.TYPE_TEXT,290,7,50,37,0,RT_HALIGN_RIGHT, '(%s)' % entry[2])
	] 
	return menu_entry


def channelEntryIPTVplaylist(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_TEXT,7,10,32,33,1,RT_HALIGN_CENTER,'%s' % entry[0]),
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 1, 35, 35, loadPNG('%s/picon35x35/%s' % (PLUGIN_PATH, entry[2]) )),
	(eListboxPythonMultiContent.TYPE_TEXT,90,7,250,22,1,RT_HALIGN_LEFT,entry[1]),
	(eListboxPythonMultiContent.TYPE_TEXT,350,7,370,22,1,RT_HALIGN_LEFT,entry[3]),  
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 90, 28, 630, 3, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH))
	]  

	return menu_entry 
	
class nKTVPlayer(Screen, InfoBarBase, InfoBarShowHide):

	skin = """
	<screen name ="nKTVPlayer" position="0,550" size="1280,190" backgroundColor="#41000000" flags="wfNoBorder" title="Kartina.TV Live">
	    <ePixmap position="80,4" size="72,36" pixmap="%(path)s/img/72x36.png" zPosition="1" transparent="0" />
		<widget position="84,7" halign="center" size="64,28" foregroundColor="#ffffff" zPosition="2" name="channel_number" transparent="1" font="RegularIPTV;34"/>
		<widget position="160,7" size="650,34" foregroundColor="#ffffff" backgroundColor="#41000000" name="channel_name" font="RegularIPTV;34"/>
		<widget position="805,10" size="300,26" halign="right" foregroundColor="#f4df8d" backgroundColor="#41000000" name="group" font="RegularIPTV;26"/>
		<widget name="picon" position="120,68" size="35,35" backgroundColor="#41000000" />
		<ePixmap position="80,50" size="117,72" pixmap="%(path)s/img/pristavka.png" zPosition="10" transparent="1" alphatest="blend" />
		
		<ePixmap position="80,125" size="126,30" pixmap="%(path)s/img/rahmen126x30.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="83,128" size="32,24" pixmap="%(path)s/img/video.png" zPosition="1" transparent="1" alphatest="blend" />
		<eLabel  position="115,133" zPosition="1" size="88,16" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="VIDEOTHEK" />		 
		
		<!-- Progressbar (current event duration)-->
		<ePixmap  pixmap="%(path)s/img/slider_1280x10_hbg.png" position="300,40" size="700,10" zPosition="3" />
		<widget name="progressbar" pixmap="%(path)s/img/slider_1280x10_hfg.png" position="300,40" size="700,10" zPosition="4" transparent="1" />

		<widget position="230,38" size="60,16" backgroundColor="#41000000" name="time_e" halign="right" foregroundColor="#fa3d3d" font="RegularIPTV;14"/> 
		<widget position="1010,38" size="80,16" backgroundColor="#41000000" name="time_l" halign="left" foregroundColor="#fa3d3d" font="RegularIPTV;14"/>

		<widget position="230,56" size="60,25" foregroundColor="#ffffff" backgroundColor="#41000000" name="time_start" font="RegularIPTV;24"/>    	
		<widget position="300,56" size="650,25" foregroundColor="#ffffff" backgroundColor="#41000000" name="programm" font="RegularIPTV;24"/>
		<widget position="950,56" halign="right" size="80,22"  backgroundColor="#41000000" name="duration" foregroundColor="#206df9" font="RegularIPTV;20"/>
		
		<widget position="300,80" size="730,20" foregroundColor="#ffffff" backgroundColor="#41000000" name="descript" font="RegularIPTV;16"/>

		<widget position="230,100" size="60,25" backgroundColor="#41000000" foregroundColor="#76addc" name="time_end" font="RegularIPTV;24"/>		 
		<widget position="300,100" size="650,27" backgroundColor="#41000000" foregroundColor="#76addc" name="next_programm" font="RegularIPTV;24"/>
		<widget position="950,102" halign="right" size="80,22" backgroundColor="#41000000" foregroundColor="#76addc" name="duration_next" font="RegularIPTV;20"/>
		
		<ePixmap position="1115,4" size="72,36" pixmap="%(path)s/img/72x36.png" zPosition="1" transparent="0" /> 
		<widget  position="1118,9" size="66,26" foregroundColor="#ffffff" halign="center" zPosition="2" name="time_now" transparent="1" font="RegularIPTV;28"/>
		<ePixmap position="1070,50" size="117,72" pixmap="%(path)s/img/picon_kartinatv117x72.png" zPosition="1" transparent="1" alphatest="blend" />
<!--
		<ePixmap position="1061,125" size="126,30" pixmap="%(path)s/img/rahmen126x30.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="1064,128" size="32,24" pixmap="%(path)s/img/tv.png" zPosition="1" transparent="1" alphatest="blend" />
		<eLabel  position="1097,133" zPosition="1" size="88,16" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="PLAYLIST" />
-->		 
		<ePixmap position="230,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="434,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="638,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="842,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />		
		<ePixmap position="235,128" size="25,25" pixmap="%(path)s/img/red.png"    zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="439,128" size="25,25" pixmap="%(path)s/img/green.png"  zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="643,128" size="25,25" pixmap="%(path)s/img/yellow.png" zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="847,128" size="25,25" pixmap="%(path)s/img/blue.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="263,130" zPosition="4" size="150,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="All Channels" />
		<eLabel position="471,130" zPosition="4" size="150,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="N-Guide" />
		<eLabel position="676,130" zPosition="4" size="150,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Categories" />
		<eLabel position="880,130" zPosition="4" size="150,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Favorites" />		
		
	</screen>""" % {'path' : PLUGIN_PATH}

  	
 	def __init__(self, session):
		Screen.__init__(self, session)
		InfoBarBase.__init__(self, steal_current_service=True)
		InfoBarShowHide.__init__(self)
		self['channel_name'] = Label('')
		self['picon'] = Pixmap()
		self['time_start'] = Label('')
		self['time_end'] = Label('')
		self['programm'] = Label('')
		self['descript'] = Label('') 
		self['time_e'] = Label('') 
		self['time_l'] = Label('') 
		self['time_now'] = Label('')
		self['next_programm'] = Label('')
		self['progressbar'] = Slider(0, 250)
		self['duration'] = Label('')
		self['duration_next'] = Label('')
		self.InfoBar_NabDialog = Label('')
		self.session = session
		self['channel_number'] = Label('')
		self['group'] = Label('')
		

		self["actions"] = HelpableActionMap(self, "nKTV",
		{   
            "left": self.prevChannel,
			"right": self.nextChannel,
			"back": self.exit_box,
			"up": self.show_channel_list,
			"down": self.show_channel_list,
			"channelPlus": self.nextGroup,
			"channelMinus": self.prevGroup,			
			"showEPGList": self.showEpg,
			"menu": self.showState,
			"power": self.power,
			"red": self.functionRed,			
			"green": self.functionGreen,
			"yellow": self.functionYellow,
			"blue": self.functionBlue,
			"tv": self.iptvplayer,
			"video": self.vodplayer,
			"help": self.iptvplayer,
			"ok": self.toggleShow,#cube fix
		}, -1)                                            
	
		self["myNumberActions"] = NumberActionMap(["NumberActions"],
		{   
 			"1": self.keyNumberGlobal,
 			"2": self.keyNumberGlobal,
 			"3": self.keyNumberGlobal,
 			"4": self.keyNumberGlobal,
 			"5": self.keyNumberGlobal,
 			"6": self.keyNumberGlobal,
 			"7": self.keyNumberGlobal,
 			"8": self.keyNumberGlobal,
 			"9": self.keyNumberGlobal,
 			"0": self.keyNumberGlobal
		}, -1)
		
		self.channel_list = KTV_API.channel_list() 
  
		self.index = 0
		self.listMode = 0
		self.gr_index = 0
		self.chID = config.plugins.ktv.last_chid.value
		for x in xrange(len(self.channel_list)):
			if self.channel_list[x][0] == config.plugins.ktv.last_chid.value:
				self.index = x
				break 
		
		self.StateTimer = eTimer()
		self.onShown.append(self.setState)
		self.StateTimer.callback.append(self.setState)
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.StandbyTimer = eTimer()
		self.StandbyTimer.callback.append(self.standByChecker)
		self.standby = 0
		self.epgTimer = eTimer()
		self.epgTimer.callback.append(self.updateEpg)
		self.onFirstExecBegin.append(self.play_channel)
		self.programmServerTime = 0
		self.next_program = []
	
	#cube fix
	def openEventView(self): 
		self.fix = ""
		
	def iptvplayer(self):
		self.session.openWithCallback(self.play_channel, IPTVplayer) 
		
	def vodplayer(self):
		self.session.openWithCallback(self.play_channel, VideothekPlaylist)		

	def functionRed(self):
		if self.listMode != 0:
			id = 0
		else:
			id = self.index
		self.session.openWithCallback(self.channel_answer, MyChannelSelection, id, 0)
	def functionGreen(self):	
		self.session.openWithCallback(self.channel_answer, MyChannelSelection, 0, 1)
	def functionYellow(self):
		if self.listMode != 2:
			id = 0
		else:
			id = self.index
		self.session.openWithCallback(self.channel_answer, MyChannelSelection, id, 2, self.gr_index)
	def functionBlue(self):
		if self.listMode != 3:
			id = 0
		else:
			id = self.index
		self.session.openWithCallback(self.channel_answer, MyChannelSelection, id, 3)

	def keyNumberGlobal(self, number):    
		self.session.openWithCallback(self.numberEntered, NumberZap, number)

	def numberEntered(self, num):
		self.index = num - 1
		if self.index >= 0:
			if self.index < len(self.channel_list):
				self.play_channel()

	def power(self):
		self.standby = 1
		self.session.open(Standby)
		self.session.nav.stopService()
		self.standByChecker()
		self.StateTimer.stop()

			
	def standByChecker(self):
		self.StandbyTimer.start(500, True)
		if self.standby == 0:
			self.StandbyTimer.stop()
			self.play_channel()   

	def setState(self):
		self.standby = 0
		STATE_API.set_state(self.chID)
		self.StateTimer.start(5000, True) 
		
	def showState(self):
		self.session.open(MyState)

	def updateEpg(self):
		update = False 
		self.epgTimer.start(1000, True)
		try:
			self.channel_list = KTV_API.channel_list()
			if self.listMode == 2:
				self.channel_list = KTV_API.groups[self.gr_index][4] 
			if self.listMode == 3:
				self.channel_list = KTV_API.favorite_chan_list
			entry = self.channel_list[self.index]

			if  self.programmServerTime < entry[9]:
				self.programmServerTime = self.programmServerTime + 1
				self['time_now'].setText("%s" % datetime.fromtimestamp(float(self.programmServerTime)).strftime('%H:%M'))
			else:
				update = True
				self.next_program = KTV_API.get_epg_next3(self.channel_list[self.index][0])
				KTV_API.channel_list_refresch()
				self.channel_list = KTV_API.channel_list()
				if self.listMode == 2:
					self.channel_list = KTV_API.groups[self.gr_index][4]
				if self.listMode == 3:
					self.channel_list = KTV_API.favorite_chan_list

			entry = []
			entry = self.channel_list[self.index]

			self.chID = entry[0]
			self['next_programm'].setText('')
			self['time_end'].setText('')
			self['duration_next'].setText('')   	   
			self['channel_name'].setText(entry[1])
			self['picon'].instance.setPixmapFromFile('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH,self.chID)) 
			self['time_start'].setText(entry[4])
			self['programm'].setText(entry[2])
			self['descript'].setText(entry[3])
			self['progressbar'].setValue(0)
			self['time_e'].setText('') 
			self['time_l'].setText('')
			self['duration'].setText('')
			self['channel_number'].setText('%i' % (self.index + 1))
			
			if entry[8]!=0:
				if entry[8] < 0:
					entry[8] = 0
				self['duration'].setText('+%i min' % entry[8])

			if entry[7]:
				self['time_e'].setText('%i min' % entry[7]) 
				self['time_l'].setText('%i %%' % entry[6])

			if entry[6]:
				self['progressbar'].setValue(int(2.5 * entry[6]))
                          
			if self.next_program[0]!='':
				self['next_programm'].setText(self.next_program[0])
				self['time_end'].setText(entry[5])
				self['duration_next'].setText('%i min' % self.next_program[2])
			self['group'].setText("[%s] %s" % (entry[19], entry[18]))
			if update:
				self.show() 
		except Exception, ex:
			print ex
			print 'updateEpg error'

# 0 - 4_3_letterbox, 1 - 4_3_panscan, 2- 16_9, 3- 16_9_always, 4 - 16_10_letterbox, 5- 16_10_panscan, 6 - 16_9_letterbox
	def play_channel(self):
		try:
			self.next_program = KTV_API.get_epg_next3(self.channel_list[self.index][0])
		except:
			self.next_program = ('','','','')
		self.updateEpg() 
		try:
			print '[channel id] %s' % self.chID 
			self.session.nav.stopService()
			url = KTV_API.getChannel_url(self.chID, None) 
			sref = eServiceReference(STREAM_ID, 0, url)
			if PANSCANon4x3 == True:
				if self.chID in ('207', '261', '295', '297', '309'):
					eAVSwitch.getInstance().setAspectRatio(0) 
					print '[16:9] [|4:3|]'
				else:
					eAVSwitch.getInstance().setAspectRatio(2)
					print '[4:3] ->  [16:9]'
			self.session.nav.playService(sref)
			self.programmServerTime = int(KTV_API.servertime)
		except:
			self.session.open(MessageBox,_("LOGIN ERROR"), type=MessageBox.TYPE_ERROR)
		
	def show_channel_list(self):
		self.session.openWithCallback(self.channel_answer, MyChannelSelection, self.index, self.listMode, self.gr_index)   

	def channel_answer(self, index = None, listMode=None, gr_index=None):
		if gr_index > -1:
			self.gr_index = gr_index
		if listMode > -1:	
			self.listMode = listMode
		if index > -1:
			self.index = index		
			self.play_channel()
		  
	def nextChannel(self):  
		self.index +=1
		if self.index == len(self.channel_list):
			self.index = 0          
		self.play_channel() 

	def prevChannel(self):
		self.index -=1
		if self.index == -1:
			self.index = len(self.channel_list)-1	
		self.play_channel()

	def nextGroup(self):
		if self.listMode==2:
			self.gr_index +=1
			if self.gr_index >=  len(KTV_API.groups) - 1:
				self.gr_index = 0
			self.channel_list = KTV_API.groups[self.gr_index][4]
			self.index = 0          
			self.play_channel()		

	def prevGroup(self):
		if self.listMode==2:
			self.gr_index -=1
			if self.gr_index == -1:
				self.gr_index = len(KTV_API.groups)-2
			self.channel_list = KTV_API.groups[self.gr_index][4]
			self.index = 0 	
			self.play_channel()
		
	def showEpg(self):
		self.StateTimer.stop()
		if self.channel_list:	
			self.session.openWithCallback(self.epg_answer, MyEpgSelection, self.channel_list[self.index])
		
	def epg_answer(self, archive = 0):
		if archive > 0:
			self.play_channel()

	def exit_box(self):
		self.session.openWithCallback(self.exit, MessageBox, _("Exit Plugin?"), type=MessageBox.TYPE_YESNO)

	def exit(self, message=None):  
		if message:
			self.session.nav.stopService()
			config.plugins.ktv.last_chid.value = self.chID
			config.plugins.ktv.last_chid.save()
			config.plugins.ktv.favorites.value = str(favoriteList)
			config.plugins.ktv.favorites.save()
			self.session.nav.playService(self.oldService)
			self.close()



class MyState(Screen):
	skin = """
	<screen name ="MyState" flags="wfNoBorder"  position="1150,50" size="80,650" title="Kartina.TV Online State" >
	<eLabel  position="0,0" zPosition="1" size="80,24" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;26" transparent="1" text="State" />		 
	<widget name="feedlist" selectionDisabled="1" position="0,30" size="80,626" zPosition="1" foregroundColorSelected="#ffffff" foregroundColor="#ffffff" backgroundColor="#41000000" backgroundColorSelected="#41000000" scrollbarMode="showNever" />
	</screen>""" 

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.mlist.l.setFont(0, gFont('RegularIPTV', 22))
		self.mlist.l.setItemHeight(37)  
		self["feedlist"] = self.mlist
		self.mlist.setList(map(stateEntry, STATE_API.get_state()))
		
		
		self["actions"] = HelpableActionMap(self, "nKTV",
		{   
			"back": self.exit,
			"menu": self.exit,			
			"power": self.power,
		}, -1)                 

	def power(self):
		if inStandby == None:
			session.open(Standby)
		else:
			inStandby.Power()
					
	def exit(self): 
		self.close()
		    
class MyChannelSelection(Screen):
	skin = """	
	<screen name ="MyChannelSelection" position="0,0" size="1280,720" backgroundColor="#41000000" flags="wfNoBorder" title="Kartina.TV Channellist" > 

		<widget foregroundColorSelected="#ffffff" backgroundColor="#41000000" foregroundColor="#76addc" backgroundColorSelected="#41000000" selectionPixmap="%(path)s/img/x37small.png" name="grouplist" scrollbarMode="showOnDemand" position="826,92" size="380,552" zPosition="1"  /> 
		<widget foregroundColorSelected="#ffffff" backgroundColor="#41000000" foregroundColor="#76addc" backgroundColorSelected="#41000000" selectionPixmap="%(path)s/img/x37.png"  enableWrapAround="1" name="feedlist" position="50,50" size="760,592" zPosition="1" scrollbarMode="showOnDemand" transparent="0" />   
		<widget backgroundColor="#41000000" foregroundColor="#ffffff" position="826,55" size="380,30"  name="pr_time" font="RegularIPTV;24" />  
		<widget backgroundColor="#41000000" foregroundColor="#ffffff" position="826,92" size="380,552" name="program" font="RegularIPTV;24" />
		<ePixmap position="0,700"  size="1280,11" pixmap="%(path)s/img/tab_line.png"     zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="47,668" size="92,30" pixmap="%(path)s/img/rahmen.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="52,671" size="32,24" pixmap="%(path)s/img/menu.png" zPosition="1" transparent="1" alphatest="blend" />
		<eLabel position="85,676" zPosition="1" size="50,24" halign="center" font="RegularIPTV;16" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="SETUP" />
		<ePixmap position="147,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="351,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="555,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="759,664" size="204,37" pixmap="%(path)s/img/tab_inactive.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="tab1" position="147,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<widget name="tab2" position="351,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<widget name="tab3" position="555,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<widget name="tab4" position="759,664" pixmap="%(path)s/img/tab_active.png" size="204,37" zPosition="2" backgroundColor="#ffffff" alphatest="blend" />
		<ePixmap position="155,671" size="25,25" pixmap="%(path)s/img/red.png"    zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="359,671" size="25,25" pixmap="%(path)s/img/green.png"  zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="563,671" size="25,25" pixmap="%(path)s/img/yellow.png" zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="767,671" size="25,25" pixmap="%(path)s/img/blue.png"   zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="187,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="All Channels" />
		<eLabel position="391,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="N-Guide" />
		<eLabel position="593,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Categories" />
		<eLabel position="800,673" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Favorites" />
		<ePixmap position="962,668" size="92,30" pixmap="%(path)s/img/rahmen.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="chminus" position="967,671" size="32,24" pixmap="%(path)s/img/chminus.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="chplus" position="967,671" size="32,24" pixmap="%(path)s/img/chplus.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="chtext" position="1000,676" zPosition="1" size="50,24" halign="center" font="RegularIPTV;16" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="ADD" />
		
		<widget name="time" position="1120,650" size="114,44" font="RegularIPTV;48" foregroundColor="#ffffff" backgroundColor="#000000" />
		<ePixmap position="1117,645" size="116,51" pixmap="%(path)s/img/flip_clock4.png" zPosition="3" transparent="1" alphatest="blend" />

	</screen>""" % {'path' : PLUGIN_PATH} 

	def __init__(self, session, index = None, listMode = None, gr_index = None):
		Screen.__init__(self, session)   
		self.session = session
		self.mode = 0
		self['tab1'] = Pixmap()
		self['tab2'] = Pixmap()
		self['tab3'] = Pixmap()
		self['tab4'] = Pixmap()
		self['chplus'] = Pixmap()
		self['chminus'] = Pixmap()
		self['chtext']= Label()
		self['tab1'].show()
		self['tab2'].hide()
		self['tab3'].hide()
		self['tab4'].hide()
		self["pr_time"] = Label()
		self["program"] = Label()
		self["time"] = Label()

		self.channel_list = KTV_API.channel_list()
		self.gr_index = gr_index

		self.index = index
		  
		self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.mlist.l.setFont(0, gFont('RegularIPTV', 22))
		self.mlist.l.setFont(1, gFont('RegularIPTV', 20)) 
		self.mlist.l.setFont(2, gFont('RegularIPTV', 14)) 
		self.mlist.l.setFont(3, gFont('RegularIPTV', 12))
		self.mlist.l.setItemHeight(37)  
		self["feedlist"] = self.mlist
		self.mlist.setList(map(channelEntryAll, self.channel_list))		

		self.glist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.glist.l.setFont(0, gFont('RegularIPTV', 24))
		self.glist.l.setItemHeight(37) 
		self['grouplist'] = self.glist 
		self.glist.setList(map(groupEntry, KTV_API.groups))		 
		self['grouplist'].hide()
		self.InfoBar_NabDialog = Label('')  
		  
		self.mlist.onSelectionChanged.append(self.updateTitle) 
		self.glist.onSelectionChanged.append(self.updateCategory)
				

		if self.gr_index:
			self.glist.moveToIndex(self.gr_index)

		self.mode = listMode
		
		if self.mode == 0:
			self.onFirstExecBegin.append(self.updateTitle)
			self.show_all()	 
		if self.mode == 1:
			self.onFirstExecBegin.append(self.wach_now)
		if self.mode == 2:
			self.onFirstExecBegin.append(self.show_category) 
		if self.mode == 3:
			self.channel_list = KTV_API.channel_list()
			self.onFirstExecBegin.append(self.showFavorites)
   
		self.show_porn = None 

			
		self["actions"] = HelpableActionMap(self, "nKTV", 
		{
			"ok": self.ok,
			"back": self.exit,
			"green": self.wach_now,
			"red": self.show_all,
			"yellow": self.show_category,
			"blue": self.showFavorites,
			"showEPGList": self.showEpg,
			"menu": self.setup,
			"channelPlus": self.addChanneltoFavorites,
			"channelMinus": self.delChannelfromFavorites,
			"power": self.exit,
			"left": self.mlist.pageUp,#cube fix
			"right": self.mlist.pageDown,#cube fix
		}, -1)
		
		
			
	def addChanneltoFavorites(self):
		if self.mode < 3:
			self.session.openWithCallback(self.add_favorite, MessageBox, _('Add channel to favorites?'), type=MessageBox.TYPE_YESNO)
		
	def delChannelfromFavorites(self):
		if self.mode == 3:
			self.session.openWithCallback(self.del_favorite, MessageBox, _('Delete channel from favorites?'), type=MessageBox.TYPE_YESNO)
				
	def add_favorite(self, message=None): 
		fav_id = self.channel_list[self.mlist.getSelectionIndex()][0]
		if fav_id not in favoriteList: 
			favoriteList.append(fav_id)
		else:
			self.session.open(MessageBox, _('Already exist'), type=MessageBox.TYPE_INFO, timeout = 3)
		KTV_API.favorite_list = favoriteList
		if self.mode == 3:
			self.showFavorites() 
			
	def del_favorite(self, message=None): 
		fav_id = self.channel_list[self.mlist.getSelectionIndex()][0]
		if fav_id in favoriteList: 
			favoriteList.remove(fav_id)
		KTV_API.favorite_list = favoriteList
		if self.mode == 3:
			self.showFavorites()

	def showFavorites(self):
		if self.mode == 0:
			self.mlist.moveToIndex(0)
		KTV_API.channel_list_refresch()
		KTV_API.channel_list()
		self["chtext"].setText('DEL')
		self["chplus"].hide()
		self["chminus"].show()
		try:
			self.channel_list = KTV_API.favorite_chan_list
			self.mlist.setList(map(channelEntryFav, self.channel_list))
			self.mlist.selectionEnabled(1)			  
			self['pr_time'].show()
			self['program'].show()
		except:
			self.mlist.setList([])
			self['pr_time'].hide()
			self['program'].hide()
		self['tab1'].hide()
		self['tab2'].hide()
		self['tab3'].hide()
		self['tab4'].show()
		self['grouplist'].hide()
		self.mode = 3


	def setup(self):  	
		self.session.open(KtvSetup)
		
	def updateCategory(self): 
		try:
			if self.gr_index > -1:
				self.glist.moveToIndex(self.gr_index)
				self.gr_index = -1				 
			self['pr_time'].hide()
			selected = KTV_API.groups[self.glist.getSelectionIndex()]
			self.channel_list =  selected[4] 
			self.mlist.setList(map(channelEntryCat, self.channel_list))
			self.mlist.selectionEnabled(0)
		except:
			print 'error updateCategory'
		
	def showEpg(self):  	
		self.session.open(MyEpgSelection, channel_info = self.selected) 
		
	def show_category(self):
		self['tab1'].hide()
		self['tab2'].hide()
		self['tab3'].show()
		self['tab4'].hide()  	
		self.updateCategory()
		self['grouplist'].show()
		self["chminus"].hide()
		self["chplus"].show()
		self["chtext"].setText('ADD')
		self.mode = 2 

	def wach_now(self):
		self.index = 0
		self.channel_list = KTV_API.channel_list()
		self.channel_list = KTV_API.watch_now_channels
		self['grouplist'].hide()
		self["chminus"].hide()
		self["chplus"].show()
		self["chtext"].setText('ADD')
		self['pr_time'].show()
		self.mlist.selectionEnabled(1)		
		if self.channel_list:     
			self.mlist.setList(map(channelEntryNow, self.channel_list))
			self['tab1'].hide()
			self['tab2'].show()
			self['tab3'].hide()
			self['tab4'].hide()
			self.mode = 1 
		
	def updateTitle(self):
		selected = []
		if self.mode ==3 and self.index > len(KTV_API.favorite_chan_list):
			self.index = 0				
		if self.index > -1:
			self.mlist.moveToIndex(self.index)  
			self.index = -1
		self["time"].setText(KTV_API.servertime_str)

		try:
			selected = self.channel_list[self.mlist.getSelectionIndex()]
			next_program = KTV_API.get_epg_next3(selected[0])			                         
			self.selected = selected
			text_next = ""   		                                              
			if  next_program:  
				text_next = '%s (%i min)\n%s\n%s' % (self.selected[5], next_program[2], next_program[0], next_program[1]) 
			if selected[4]!="":
				self["pr_time"].setText("%s (+ %i min )" % (selected[4],selected[8])) 
			else:
				self["pr_time"].setText("")
			descr = ""	
			if selected[3]:
				 descr = '%s\n' % selected[3]   
			self["program"].setText("%s\n%s\n%s" % (selected[2], descr, text_next))
		except:
			print 'error updateTitle'

		
	def show_all(self):
		self.mlist.selectionEnabled(1)
		self['grouplist'].hide()
		self['pr_time'].show()
		self["chminus"].hide()
		self["chplus"].show()
		self["chtext"].setText('ADD')
		self.channel_list = KTV_API.channel_list()
		if self.channel_list:
			self.mlist.setList(map(channelEntryAll, self.channel_list))
			self.mlist.moveToIndex(self.index)
			self['tab1'].show()
			self['tab2'].hide()
			self['tab3'].hide()
			self['tab4'].hide()
			self.mode = 0

		
	def ok(self):
		ch_index = self.mlist.getSelectionIndex()
		if self.mode == 2: 
			self.mlist.selectionEnabled(1)
			self['grouplist'].hide()
			self['pr_time'].show()
			self.mlist.moveToIndex(0)
			if (self.show_porn == None) and (self.glist.getSelectionIndex() == len(KTV_API.groups)-1):
				self.myPassInput()
			else:
				self.mode = 20   
		elif self.mode == 20:   
			gr_index = self.glist.getSelectionIndex()
			self.close(ch_index, 2, gr_index)
		elif self.mode == 1:
			temp_channel_list = self.channel_list
			self.channel_list = KTV_API.channel_list()
			for x in xrange(len(self.channel_list)):
					if self.channel_list[x] == temp_channel_list[ch_index]:
						ch_index = x
						break
			self.close(ch_index, 0, 0)
		else: 
			self.close(ch_index, self.mode, 0)

	def myPassInput(self):
		self.session.openWithCallback(self.checkPasswort, InputBox, 
		title=_("Please enter a passwort"), text="*" * 4, maxSize=4,
		type=Input.PIN) 
		
	def checkPasswort(self, number):
		a = '%s' % number
		b = '%s' % PORNOPASS
		if a == b:
			self.show_porn = True 
			self.mode = 20
   
	def exit(self):
		self.close()		


class MyEpgSelection(Screen):
	skin = """	
	<screen name ="MyEpgSelection" position="0,0" size="1280,720" backgroundColor="#41000000" flags="wfNoBorder"  title="Kartina.TV EPG" >
		<widget foregroundColorSelected="#ffffff" backgroundColor="#41000000" foregroundColor="#76addc" enableWrapAround="1" backgroundColorSelected="#41000000" selectionPixmap="%(path)s/img/x37.png" name="feedlist" position="50,50" size="760,592" zPosition="1" scrollbarMode="showOnDemand" transparent="1"  />   
		<widget backgroundColor="#41000000" foregroundColor="#ffffff" position="826,140" size="380,552" name="program" font="RegularIPTV;26"/>   
		<widget name="picon" position="110,650" size="35,35" backgroundColor="#41000000" />                                                                   
		<widget position="160,649" size="626,38" valign="center" foregroundColor="#fffffff" backgroundColor="#20000000" name="channel_name" font="RegularIPTV;38"/>
		<widget name="time" position="1120,650" size="114,44" font="RegularIPTV;48" foregroundColor="#ffffff" backgroundColor="#000000" />
		<ePixmap position="1117,645" size="116,51" pixmap="%(path)s/img/flip_clock4.png" zPosition="3" transparent="1" alphatest="blend" />  
		
		<ePixmap position="918,48" size="208,70" pixmap="%(path)s/img/flip_calender.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget  position="918,52" size="208,30" foregroundColor="#fffffff" backgroundColor="#41000000" zPosition="3" transparent="1" halign="center" name="pr_time" font="RegularIPTV;30" />
		<widget  position="918,83" size="208,30" foregroundColor="#fffffff" backgroundColor="#41000000" zPosition="3" transparent="1" halign="center" name="pr_day" font="RegularIPTV;30" />
		<ePixmap name="ramka1" position="826,50" size="92,30" pixmap="%(path)s/img/rahmen.png" backgroundColor="#ffffff" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="chminus" position="829,52" size="32,24" pixmap="%(path)s/img/chminus.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="chprev"  position="864,57" zPosition="1" size="50,18" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="PREV" />   	
		<ePixmap name="ramka2" position="1125,50" size="92,30" pixmap="%(path)s/img/rahmen.png" backgroundColor="#ffffff" zPosition="1" transparent="1" alphatest="blend" />  
		<widget name="chplus"  position="1128,52" size="32,24" pixmap="%(path)s/img/chplus.png" zPosition="1" transparent="1" alphatest="blend" />
		<widget name="chnext"  position="1163,57" zPosition="1" size="50,18" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="NEXT" />
		<widget position="780,649" size="300,38" halign="right" valign="center" foregroundColor="#fffffff" backgroundColor="#20000000" name="epgtext" font="RegularIPTV;30"/>
		
	</screen>""" % {'path' : PLUGIN_PATH}


	def __init__(self, session, channel_info, arch_position = None, epg_day_position = None):
		Screen.__init__(self, session)   

		self.skin = MyEpgSelection.skin
		self.session = session
		self.archive = 0

		self.channel_info = channel_info
		self.arch_position = arch_position
		self.epg_day_position = epg_day_position 
		 
		self.mlist = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.mlist.l.setFont(0, gFont('RegularIPTV', 22))
		self.mlist.l.setFont(1, gFont('RegularIPTV', 20)) 
		self.mlist.l.setItemHeight(37) 

		self["feedlist"] = self.mlist
		self["pr_time"] = Label()
		self["program"] = Label()  
		self["picon"] = Pixmap()
		self["channel_name"] = Label()
		self["time"] = Label()
		self["chminus"] = Pixmap()
		self["chplus"] = Pixmap()
		self["chnext"] = Label()
		self["chprev"] = Label()
		self["epgtext"] = Label()
		self["pr_day"] = Label()
		self.InfoBar_NabDialog = Label('') 
		self.epg_day = 0
		


		self.programm_list = KTV_API.get_epg(self.channel_info[0], '%s' % KTV_API.servertime_date , self.channel_info) 

		if self.programm_list:
			self.mlist.setList(map(epgEntry, self.programm_list))     
			self.onFirstExecBegin.append(self.updateEpgDescr)
			self.onFirstExecBegin.append(self.setSelected)
			self.onFirstExecBegin.append(self.epgStart)
			self.mlist.onSelectionChanged.append(self.updateEpgDescr)
		else:
			self.exit()	

		self["actions"] = HelpableActionMap(self, "nKTV",
		{
			"back": self.exit,
			"showEPGList": self.exit,
			"power": self.exit,
			"ok": self.ok,
			"channelPlus": self.nextDay,
			"channelMinus": self.prevDay,
			"left": self.mlist.pageUp,#cube fix
			"right": self.mlist.pageDown,#cube fix
		}, -1)


	def epgStart(self):
		if self.epg_day_position > -14:
			self.epg_day = self.epg_day_position 
			date = (datetime.fromtimestamp(float(KTV_API.servertime)) + timedelta(days=self.epg_day)).strftime("%d%m%y")
			self.programm_list = KTV_API.get_epg(self.channel_info[0], '%s' % date, self.channel_info)
			self.showEpg()
			
	def prevDay(self):
		self.epg_day -= 1
		if self.epg_day< -13:
			self.epg_day = -13  
		self.showEpg()

	def nextDay(self):
		self.epg_day += 1
		self.showEpg()
		
	def setSelected(self): 
		if KTV_API.epg_id >-1:
			self.mlist.moveToIndex(KTV_API.epg_id)
		else:
			self.mlist.moveToIndex(0)
		if self.arch_position:
			self.mlist.moveToIndex(self.arch_position)

	def updateEpgDescr(self):
 
		self["picon"].instance.setPixmapFromFile('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH,self.channel_info[0])) 
		self["channel_name"].setText('  %s' % self.channel_info[1])
		self["epgtext"].setText('EPG ')
		self["time"].setText(KTV_API.servertime_str)
		try:
			if self.programm_list:
				selected = self.programm_list[self.mlist.getSelectionIndex()]
				self.epg_selected = selected 
				self.full_epg = self.programm_list 
				self.full_epg_index = self.mlist.getSelectionIndex()   
				program = ""
				description = ""
				if selected[1]:
					program = selected[1]
					if selected[2]:
						description = selected[2]                          

				self["pr_time"].setText("%s" % selected[4])
				self["pr_day"].setText(_("%s" % selected[7]))   
				self["program"].setText("%s\n%s" % (program, description))
		except:
			print 'updateEpgDescr error'



	def showEpg(self): 
		if not self.channel_info[12] and self.epg_day < 0:
			self.epg_day = 0  
		date = (datetime.fromtimestamp(float(KTV_API.servertime)) + timedelta(days=self.epg_day)).strftime("%d%m%y")
		
		self.programm_list = KTV_API.get_epg(self.channel_info[0], '%s' % date, self.channel_info)
		
		date_next = (datetime.fromtimestamp(float(KTV_API.servertime)) + timedelta(days=self.epg_day+1)).strftime("%d%m%y")
		KTV_API.get_epg_first_time(self.channel_info[0], '%s' % date_next)  

		if self.programm_list: 			
			self.mlist.setList(map(epgEntry, self.programm_list))
			self.setSelected()

								
			self.updateEpgDescr
		elif self.epg_day==0:
			self.mlist.setList([])
		elif self.epg_day > 0:
			self.epg_day -= 1
		else:
			self.epg_day += 1
		
	def exit(self):
		self.epg_day = 0
		self.close(self.archive)
	
	def archive_answer(self, archive):
		if archive:
			self.close(1)

	def ok(self):
		if self.epg_selected[0] <  KTV_API.servertime and self.channel_info[12]:			
			self.session.openWithCallback(self.archive_answer, IPTV_Archive_Player, channel = self.channel_info, archiveTime = self.epg_selected[0], fullEpg = self.full_epg, fullEpgIndex = self.full_epg_index, epg_day = self.epg_day)


class IPTV_Archive_Player(Screen, InfoBarBase, InfoBarShowHide): 

	skin = """
	<screen name ="IPTV_Archive_Player" position="0,550" size="1280,190" backgroundColor="#41000000" flags="wfNoBorder" title="Kartina.TV Archive">
		<widget position="80,10" size="700,26" foregroundColor="#ffffff" backgroundColor="#41000000" name="channel_name" font="RegularIPTV;26"/>
		<widget name="picon" position="120,58" size="35,35" backgroundColor="#41000000" />
		<ePixmap position="80,40" size="117,72" pixmap="%(path)s/img/pristavka.png" zPosition="10" transparent="1" alphatest="blend" /> 
		<ePixmap position="80,116" size="117,23" pixmap="%(path)s/img/archive.png" zPosition="1" transparent="0" />
		<!-- Progressbar (current event duration)-->
		<ePixmap  pixmap="%(path)s/img/slider_1280x10_hbg.png" position="300,40" size="700,10" zPosition="3" />
		<widget name="progressbar" pixmap="%(path)s/img/slider_1280x10_hfg.png" position="300,40" size="700,10" zPosition="4" transparent="1" />
		<widget name="flag"  pixmap="%(path)s/img/flag.png" position="1300,1300" size="60,16" zPosition="1" transparent="0" />
		<widget name="progress_time" position="1300,1300" halign="left" size="60,14" backgroundColor="#41000000" foregroundColor="#ffffff" zPosition="1" transparent="1" font="RegularIPTV;14"/>

		<widget position="230,38" size="60,16" backgroundColor="#41000000" name="time_e" halign="right" foregroundColor="#fa3d3d" font="RegularIPTV;14"/> 
		<widget position="1010,38" size="80,16" backgroundColor="#41000000" name="time_l" halign="left" foregroundColor="#fa3d3d" font="RegularIPTV;14"/>

		<widget position="230,56" size="60,25" foregroundColor="#ffffff" backgroundColor="#41000000" name="time_start" font="RegularIPTV;24"/>    	
		<widget position="300,56" size="630,25" foregroundColor="#ffffff" backgroundColor="#41000000" name="programm" font="RegularIPTV;24"/>
		<widget position="930,56" halign="right" size="110,22"  backgroundColor="#41000000" name="time_left" foregroundColor="#206df9" font="RegularIPTV;20"/>

		<widget position="230,80" size="768,60" foregroundColor="#ffffff" backgroundColor="#41000000" name="descript" font="RegularIPTV;13"/>

		<widget position="920,10" size="320,26" foregroundColor="#ffffff" backgroundColor="#41000000" halign="right" name="day_arch" font="RegularIPTV;26"/>
		
		<ePixmap position="1050,50" size="92,30" pixmap="%(path)s/img/rahmen.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="1053,53" size="32,24" pixmap="%(path)s/img/play.png" zPosition="1" transparent="1" alphatest="blend" />
		<eLabel  position="1090,58" zPosition="1" size="50,18" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="Play" />

		<ePixmap position="1150,50" size="92,30" pixmap="%(path)s/img/rahmen.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="1153,53" size="32,24" pixmap="%(path)s/img/pause.png" zPosition="1" transparent="1" alphatest="blend" />
		<eLabel  position="1190,58" zPosition="1" size="50,18" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="Pause" />

		<ePixmap position="1050,85" size="92,30" pixmap="%(path)s/img/rahmen.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="1053,88" size="32,24" pixmap="%(path)s/img/right.png" zPosition="1" transparent="1" alphatest="blend" />
		<eLabel  position="1090,93" zPosition="1" size="50,18" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="NEXT" />
				
		<ePixmap position="1150,85" size="92,30" pixmap="%(path)s/img/rahmen.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="1153,88" size="32,24" pixmap="%(path)s/img/left.png" zPosition="1" transparent="1" alphatest="blend" />
		<eLabel  position="1190,93" zPosition="1" size="50,18" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;16" transparent="1" text="PREV" />

		<!-- <ePixmap position="1050,120" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" /> -->
		<!-- <eLabel  position="1050,124" zPosition="1" size="192,32" halign="center" foregroundColor="#ffffff" backgroundColor="#41000000" font="RegularIPTV;22" transparent="1" text="" /> -->

		<ePixmap position="220,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="424,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="628,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="832,125" size="192,30" pixmap="%(path)s/img/rahmen_big.png" zPosition="1" transparent="1" alphatest="blend" />		
		<ePixmap position="429,128" size="32,24" pixmap="%(path)s/img/chplus.png"  zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="525,128" size="32,24" pixmap="%(path)s/img/chminus.png"  zPosition="3" transparent="1" alphatest="blend" />		
		<ePixmap position="633,128" size="32,24" pixmap="%(path)s/img/right_0.png" zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="727,128" size="32,24" pixmap="%(path)s/img/left_0.png" zPosition="3" transparent="1" alphatest="blend" />		
		<ePixmap position="837,128" size="32,24" pixmap="%(path)s/img/ff.png"   zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="931,128" size="32,24" pixmap="%(path)s/img/rw.png"   zPosition="3" transparent="1" alphatest="blend" />		
		<eLabel position="224,130" zPosition="4" size="184,20" halign="center" font="RegularIPTV;22" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="0-9 > 0-90 %%" />		
		<eLabel position="464,131" zPosition="4" size="58,20" halign="left" font="RegularIPTV;18" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="+1 min" />
		<eLabel position="563,131" zPosition="4" size="50,20" halign="left" font="RegularIPTV;18" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="-1 min" />
		<eLabel position="668,131" zPosition="4" size="58,20" halign="left" font="RegularIPTV;18" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="+3 min" />
		<eLabel position="763,131" zPosition="4" size="50,20" halign="left" font="RegularIPTV;18" transparent="0" foregroundColor="#ffffff" backgroundColor="#41000000" text="-3 min" />
		<eLabel position="872,133" zPosition="4" size="58,20" halign="left" font="RegularIPTV;16" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="+10 min" />
		<eLabel position="967,133" zPosition="4" size="54,20" halign="left" font="RegularIPTV;16" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="-10 min" />		


	</screen>""" % {'path' : PLUGIN_PATH}
	
	def __init__(self, session, channel=None, archiveTime = None, fullEpg = None, fullEpgIndex = None, epg_day = None):
		Screen.__init__(self, session)
		InfoBarBase.__init__(self, steal_current_service=True)
		InfoBarShowHide.__init__(self)
		self['channel_name'] = Label('')
		self['picon'] = Pixmap()
		self['flag'] = Pixmap()
		self['time_start'] = Label('')
		self['programm'] = Label('')
		self['descript'] = Label('') 
		self['time_e'] = Label('') 
		self['time_l'] = Label('') 
		self['day_arch'] = Label('')
		self['progressbar'] = Slider(0, 250)
		self['time_left'] = Label('')
		self['progress_time'] = Label('')
		self.mode = 0
		self.arch_time_start = 0
		self.arch_timer = 0
		self.time_start = 0
		self.one_percent_second = 0
		self.pause_time = 0
		self.InfoBar_NabDialog = Label('')
		self.epg_day = epg_day
		
		self["myNumberActions"] = NumberActionMap(["NumberActions"],
		{   
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal
		}, -1) 
		
		self["actions"] = HelpableActionMap(self, "nKTV",
		{   
 			"left": self.prevChannel,
			"right": self.nextChannel,
			"channelPlus": self.channelPlus,
			"channelMinus": self.channelMinus,
			"fforward": self.fforward,
			"rewind": self.rewind,  
			"blue": self.fforward,
			"red": self.rewind,			
			"next": self.next,
			"previous": self.previous,
			"up": self.showEpg,
			"back": self.exit,
			"showEPGList": self.showEpg,
			"playpauseService": self.play_service,
			"pauseService": self.pause_service,
			"green": self.play_service,
			"yellow": self.pause_service,
			"power": self.power,
			"ok": self.toggleShow,#cube fix 
		}, -1)
				                                           
		self.channel = channel
		self.full_epg = fullEpg
		self.full_epg_index = fullEpgIndex
		self.time = archiveTime
		self.epg_counter = len(self.full_epg)

		self.StateTimer = eTimer()
		self.StateTimer.callback.append(self.setState)
		self.onShown.append(self.archEpg)
		self.onFirstExecBegin.append(self.play_channel_start)
		self.onShown.append(self.setState)
		self.StandbyTimer = eTimer()
		self.StandbyTimer.callback.append(self.standByChecker)
		self.standby = 0
		self.epgTimer = eTimer()
		self.epgTimer.callback.append(self.archEpg)

	#cube fix
	def openEventView(self): 
		self.fix = ""
			
	def showEpg(self):
		self.StateTimer.stop() 	
		self.session.openWithCallback(self.exit_answer, MyEpgSelection, self.channel, self.full_epg_index, self.epg_day)

	def exit_answer(self, mode = None):
		if mode:
			self.close(1)

	def power(self):
		self.standby = 1
		self.session.open(Standby)
		self.pause_service()
		self.standByChecker()
		self.StateTimer.stop()

	def standByChecker(self):
		self.StandbyTimer.start(500, True)
		if self.standby == 0:
			self.StandbyTimer.stop()
			self.play_service()   

	def setState(self):
		self.standby = 0
		STATE_API.set_state_archive(self.channel[0])
		self.StateTimer.start(5000, True)
	
	def channelPlus(self):
		self.plusMinus(1)
		   
	def channelMinus(self):
		self.plusMinus(-1)
		   
	def fforward(self):
		self.plusMinus(10)
		
	def rewind(self):
		self.plusMinus(-10)
		 
	def next(self):
		self.plusMinus(3)
		
	def previous(self):
		self.plusMinus(-3)
		
	def plusMinus(self, myNumber):   
		self.mode = 1 
		self.arch_timer = int(time()) - int(self.arch_time_start)
		new_time = myNumber*60 + self.arch_timer + int(self.time) 
		self.time =  '%i' % new_time
		
		selected = self.full_epg[self.full_epg_index]
		if self.time < selected[0] and self.full_epg_index > 1 :
			self.full_epg_index = self.full_epg_index -1
		else:
			if self.full_epg_index < len(self.full_epg) -1:
				selected_next = self.full_epg[self.full_epg_index+1]
				if self.time > selected_next[0]: 	
						self.full_epg_index = self.full_epg_index +1
   
		self.play_channel()

	def play_service(self):
		if self.mode == 3: 
			self.time = self.pause_time
			self.mode = 4
			self.play_channel()
		
	def pause_service(self):
		if self.mode != 3:
			self.arch_timer = int(time()) - int(self.arch_time_start)
			self.pause_time = int(self.time) + self.arch_timer - 5
			self.session.nav.pause(True) 
			self.mode = 3
			   
	def keyNumberGlobal(self, number):
		self.mode = 1   
		new_time =  int( int(self.time_start) + number * 10 * self.one_percent_second)
		self.time = "%i" % new_time
		self.play_channel()
	
	def play_channel_start(self):
		self.archEpg()
		self.mode = 1
		self.play_channel()

	def archEpg(self):

		if self.mode == 1:			
			if self.full_epg_index < len(self.full_epg) -1:
				selected_next = self.full_epg[self.full_epg_index+1]
				if self.time > selected_next[0]: 	
						self.full_epg_index = self.full_epg_index +1
						self.show()	
		self.epgTimer.start(1000, True)
		if self.full_epg_index ==  self.epg_counter:
			selected = self.full_epg[self.full_epg_index]
			self.full_epg_index = 0
			self.time = selected[0]
		if self.full_epg_index == -1 :
			self.full_epg_index = self.epg_counter -1
			selected = self.full_epg[self.full_epg_index]
			self.time = selected[0]
				
		if self.mode != 4: 
			self.arch_timer = int(time()) - int(self.arch_time_start)
			new_time = self.arch_timer + int(self.time) 
			self.time =  '%i' % new_time

		self['channel_name'].setText(self.channel[1])
		self['picon'].instance.setPixmapFromFile('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH,self.channel[0]))
		selected = self.full_epg[self.full_epg_index]
		if self.mode == 1:
			self.time_start = selected[0]						
		if self.mode == 0:	
			self.time = selected[0]
			self.time_start = selected[0]
			self.mode = 0
		self.arch_time_start = time()
			
		program = ""
		description = ""
		duration = 0
		time_left = 0
		time_l_procent = 0
		percent = 0
		elapsed_time_min = 0

		if selected[1]:
			program = selected[1]
			if selected[2]:
				description = selected[2]
				
		day_arch = datetime.fromtimestamp(float(selected[0])).strftime('%d')
		month_arch = datetime.fromtimestamp(float(selected[0])).strftime('%b')
		week_day_arch = datetime.fromtimestamp(float(selected[0])).strftime('%A')
		
		if self.full_epg_index < (self.epg_counter -1):
			selected_next = self.full_epg[self.full_epg_index+1]
			program_end = selected_next[0]
		else: 
			program_end = KTV_API.nextday_epg_ut_start
		duration = int((int(program_end)-int(selected[0]))/60)
		time_left = int((int(program_end)-int(self.time))/60)
		elapsed_time = int(int(self.time) - int(selected[0]))
		elapsed_time_min = int(elapsed_time/60)
		percent = int(int(program_end)-int(selected[0]))/100
		self.one_percent_second = percent
		if percent!=0:
			percent = elapsed_time/percent
   
				
		self["time_start"].setText("%s" % (selected[3]))   
		self["programm"].setText("%s" % program)
		self["descript"].setText("%s" % description)
		self['day_arch'].setText(_("%s" % week_day_arch )+ ' ' + day_arch +  '. ' + _("%s" % month_arch ))		 
		self['progressbar'].setValue(int(2.5 * percent))
		self['time_e'].setText('%i min' % elapsed_time_min)
		self['progress_time'].setText(datetime.fromtimestamp(float(self.time)).strftime('%H:%M:%S'))
		self['progress_time'].setPosition(306 + int(7 * percent), 24)   
		self['flag'].setPosition(300 + int(7 * percent), 22)
		if percent < 0:
			self['progress_time'].setPosition(306, 24)
			self['flag'].setPosition(300, 22)
		if percent > 100:
			self['progress_time'].setPosition(1006, 24)
			self['flag'].setPosition(1000, 22)
			percent = 100   	    	
		self['time_l'].setText('%i %%' % percent)
		self['time_left'].setText('+ %i min' % time_left)
		

	def play_channel(self):
		self.archEpg()
		if self.mode == 4:
			self.mode = 1 
		if self.mode == 0:
			self.mode = 1			
		self.session.nav.stopService()		
		url = KTV_API.getChannel_url(self.channel[0], self.time)
		if url: 
			sref = eServiceReference(STREAM_ID, 0, url)   
			self.session.nav.playService(sref) 
		else:
			self.exit()
		
		
	def nextChannel(self):
		self.mode = 0  
		self.full_epg_index +=1
		if self.full_epg_index ==  self.epg_counter:
			self.full_epg_index = 0
		self.play_channel()		


	def prevChannel(self):
		self.mode = 0
		self.full_epg_index -=1
		if self.full_epg_index == -1 :
			self.full_epg_index = int("%s" % self.epg_counter)-1            
		self.play_channel()


	def exit(self):
		self.StateTimer.stop()
		self.close(1)


def stateEntry(entry):  
	state_entry = [entry,
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 1, 1, 35, 35, loadPNG('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH, entry[0]) )),
	(eListboxPythonMultiContent.TYPE_TEXT,36,7,34,24,0,RT_HALIGN_RIGHT,entry[1])
	] 
	return state_entry
					
def epgEntry(entry):
	img = 'clock'
	percent = 0
	percent_text = "" 
	if entry[0] <  KTV_API.servertime and entry[5]:
		img = 'rec'
		percent = 100
	if entry[6]:
	   percent = entry[6]
	   percent_text ='%i %%' % percent   	   
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 35, 35, loadPNG('%s/img/%s.png' % (PLUGIN_PATH, img) )),
	(eListboxPythonMultiContent.TYPE_TEXT,50,8,100,24,0,RT_HALIGN_LEFT,entry[3]),  
	(eListboxPythonMultiContent.TYPE_TEXT,130,8,660,24,0,RT_HALIGN_LEFT,entry[1]),
	(eListboxPythonMultiContent.TYPE_TEXT,687,7,40,22,1,RT_HALIGN_RIGHT, percent_text),
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 130, 28, 538, 3, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH)),
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 130, 28, int(5.38*percent), 3, loadPNG('%s/img/slider_1280x10_hfg.png' % PLUGIN_PATH)) 
	]

	return menu_entry

def groupEntry(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_TEXT,5,7,60,37,0,RT_HALIGN_LEFT,entry[0]),
	(eListboxPythonMultiContent.TYPE_TEXT,40,7,255,37,0,RT_HALIGN_LEFT,entry[1]),  
	(eListboxPythonMultiContent.TYPE_TEXT,290,7,50,37,0,RT_HALIGN_RIGHT, '(%s)' % entry[3])
	] 
	return menu_entry
				
def channelEntryAll(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 1, 35, 35, loadPNG('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH, entry[0]) )),
	(eListboxPythonMultiContent.TYPE_TEXT,84,3,60,22,1,RT_HALIGN_LEFT,entry[4]),  
	(eListboxPythonMultiContent.TYPE_TEXT,90,21,60,14,2,RT_HALIGN_LEFT,entry[5]), 
	(eListboxPythonMultiContent.TYPE_TEXT,140,7,200,22,1,RT_HALIGN_LEFT,entry[1]),
	(eListboxPythonMultiContent.TYPE_TEXT,350,7,300,22,1,RT_HALIGN_LEFT,entry[2]),  
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 140, 28, 568, 3, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH))
	]  
	if entry[6]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 140, 28, int(5.68*entry[6]), 3, loadPNG('%s/img/slider_1280x10_hfg.png' % PLUGIN_PATH)))
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,667,7,40,22,1,RT_HALIGN_RIGHT,'%i %%' % entry[6]))
	if entry[12]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 712, 5, 15, 26, loadPNG('%s/img/rec_small.png' % PLUGIN_PATH)))
	if entry[15]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,7,10,32,33,1,RT_HALIGN_CENTER,'%i' % entry[15]))
				 	
	return menu_entry

def channelEntryCat(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 1, 35, 35, loadPNG('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH, entry[0]) )),
	(eListboxPythonMultiContent.TYPE_TEXT,84,3,60,22,1,RT_HALIGN_LEFT,entry[4]),  
	(eListboxPythonMultiContent.TYPE_TEXT,90,21,60,14,2,RT_HALIGN_LEFT,entry[5]), 
	(eListboxPythonMultiContent.TYPE_TEXT,140,7,200,22,1,RT_HALIGN_LEFT,entry[1]),
	(eListboxPythonMultiContent.TYPE_TEXT,350,7,300,22,1,RT_HALIGN_LEFT,entry[2]),  
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 140, 28, 568, 3, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH))
	]  
	if entry[6]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 140, 28, int(5.68*entry[6]), 3, loadPNG('%s/img/slider_1280x10_hfg.png' % PLUGIN_PATH)))
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,667,7,40,22,1,RT_HALIGN_RIGHT,'%i %%' % entry[6]))
	if entry[12]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 712, 5, 15, 26, loadPNG('%s/img/rec_small.png' % PLUGIN_PATH)))
	if entry[16]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,7,10,32,33,1,RT_HALIGN_CENTER,'%i' % entry[16]))
				 	
	return menu_entry

def channelEntryFav(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 1, 35, 35, loadPNG('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH, entry[0]) )),
	(eListboxPythonMultiContent.TYPE_TEXT,84,3,60,22,1,RT_HALIGN_LEFT,entry[4]),  
	(eListboxPythonMultiContent.TYPE_TEXT,90,21,60,14,2,RT_HALIGN_LEFT,entry[5]), 
	(eListboxPythonMultiContent.TYPE_TEXT,140,7,200,22,1,RT_HALIGN_LEFT,entry[1]),
	(eListboxPythonMultiContent.TYPE_TEXT,350,7,300,22,1,RT_HALIGN_LEFT,entry[2]),  
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 140, 28, 568, 3, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH))
	]  
	if entry[6]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 140, 28, int(5.68*entry[6]), 3, loadPNG('%s/img/slider_1280x10_hfg.png' % PLUGIN_PATH)))
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,667,7,40,22,1,RT_HALIGN_RIGHT,'%i %%' % entry[6]))
	if entry[12]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 712, 5, 15, 26, loadPNG('%s/img/rec_small.png' % PLUGIN_PATH)))
	if entry[17]:
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,7,10,32,33,1,RT_HALIGN_CENTER,'%i' % entry[17]))
				 	
	return menu_entry
	 
def channelEntryNow(entry): 
	interval = KTV_API.time_show_now
	next_program = KTV_API.get_epg_next3(entry[0])
	time = None
	
	menu_entry = [entry, 
	(eListboxPythonMultiContent.TYPE_TEXT,42,4,120,22,2,RT_HALIGN_LEFT,entry[1]),
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 2, 1, 35, 35, loadPNG('%s/picon35x35/kartinatv_%s.png' % (PLUGIN_PATH, entry[0]) )),
	]  
	if interval >= entry[7] and entry[7]>=0:
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,40,20,140,22,2,RT_HALIGN_LEFT,'%s - %s (%s min)' % (entry[4], entry[5], entry[10])))  
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,180,10,400,22,1,RT_HALIGN_LEFT,entry[2]))
		if entry[7]==0:
		   time = _('now') 
		else:
		   time = '%i %%' % entry[6]
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,630,10,90,22,1,RT_HALIGN_RIGHT,time))   
	elif next_program: 
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,40,20,140,22,2,RT_HALIGN_LEFT,'%s - %s (%s min)' % (next_program[3], next_program[4], next_program[2])))  
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,180,10,400,22,1,RT_HALIGN_LEFT,next_program[0]))
		if entry[8]==0:
		   time = _('now') 
		else:
		   time = _('in') + ' %i min' % entry[8]				
		menu_entry.append((eListboxPythonMultiContent.TYPE_TEXT,570,10,90,22,1,RT_HALIGN_RIGHT, time))

	menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 180, 28, 480, 3, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH)))
	if entry[7] and time != _('now'):
		menu_entry.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 180, 28, int(4.8*entry[6]), 3, loadPNG('%s/img/slider_1280x10_hfg.png' % PLUGIN_PATH)))	 
 	
	return menu_entry

def channelEntryIPTVplaylist(entry):  
	menu_entry = [entry,
	(eListboxPythonMultiContent.TYPE_TEXT,7,10,32,33,1,RT_HALIGN_CENTER,'%s' % entry[0]),
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 40, 1, 35, 35, loadPNG('%s/picon35x35/%s' % (PLUGIN_PATH, entry[2]) )),
	(eListboxPythonMultiContent.TYPE_TEXT,90,7,250,22,1,RT_HALIGN_LEFT,entry[1]),
	(eListboxPythonMultiContent.TYPE_TEXT,350,7,370,22,1,RT_HALIGN_LEFT,entry[3]),  
	(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 90, 28, 630, 3, loadPNG('%s/img/slider_1280x10_hbg.png' % PLUGIN_PATH))
	]  

	return menu_entry
	
class KtvSetup(Screen, ConfigListScreen):

	skin = """	
	<screen name ="KtvSetup" position="center,center" size="512,400" backgroundColor="#41000000"  flags="wfNoBorder" >
		<widget position="0,10" size="512,24" halign="center" name="packet_name" font="RegularIPTV;23" transparent="0" backgroundColor="#41000000" foregroundColor="#ffffff"/>
		<widget position="0,40" size="512,24" halign="center" name="packet_expire" font="RegularIPTV;23" transparent="0" backgroundColor="#41000000" foregroundColor="#ffffff"/>
		<widget name="config" itemHeight="30" position="40,90" size="432,300" backgroundColor="#41000000" foregroundColor="#ffffff" /> 
		<ePixmap position="0,389"  size="512,11" pixmap="%(path)s/img/tab_line.png"   zPosition="1" transparent="1" alphatest="blend" />
		<ePixmap position="50,353" pixmap="%(path)s/img/tab_active.png" size="204,37" backgroundColor="#41000000" zPosition="1" alphatest="blend" />
		<ePixmap position="258,353" pixmap="%(path)s/img/tab_active.png" size="204,37" backgroundColor="#41000000" zPosition="1" alphatest="blend" />
		<ePixmap position="60,359" size="25,25" pixmap="%(path)s/img/red.png" zPosition="3" transparent="1" alphatest="blend" />
		<ePixmap position="268,359" size="25,25" pixmap="%(path)s/img/green.png" zPosition="3" transparent="1" alphatest="blend" />
		<eLabel position="80,361" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" text="CANCEL" />
		<eLabel position="288,361" zPosition="4" size="140,24" halign="center" font="RegularIPTV;22" transparent="1" text="SAVE" />
	</screen>""" % {'path' : PLUGIN_PATH}

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self["actions"] = HelpableActionMap(self, "nKTV", 
		{
			'green': self.save,
			'red': self.cancel,
			'back': self.cancel
		}, 
		-1)
		self.list = []
		self.list.append(getConfigListEntry(_('login'), config.plugins.ktv.login))
		self.list.append(getConfigListEntry(_('password'), config.plugins.ktv.password))
		self.list.append(getConfigListEntry(_('use servicewebts'), config.plugins.ktv.servicewebts))
		self.list.append(getConfigListEntry(_('N-Guide time'), config.plugins.ktv.time_show_now))
		self.list.append(getConfigListEntry(_('Start MODE'), config.plugins.ktv.start_mode))
		self.list.append(getConfigListEntry(_('Panscan'), config.plugins.ktv.panscan))  
		ConfigListScreen.__init__(self, self.list, session)
		self["packet_name"] = Label()
		self["packet_expire"] = Label()
		
		if PLUGINMODE < 2:
			date = datetime.fromtimestamp(float(KTV_API.packet_expire)).strftime('%d-%m-%Y')
			self["packet_name"].setText("Packet Name:  %s" % KTV_API.packet_name)
			self["packet_expire"].setText("Packet Expire Date: %s" % date)

	def save(self):
		for x in self["config"].list:
			x[1].save()
			self.close(True,self.session)

	def cancel(self):
		for x in self['config'].list:
			x[1].cancel()
		self.close()	


def Plugins(**kwargs):
    return [PluginDescriptor(name = "nKTVplayer", description="plugin to watch kartina.tv, kartina.vod & videostreams", where = PluginDescriptor.WHERE_MENU, fnc = menu),
	PluginDescriptor(name = "nKTVplayer", description="plugin to watch kartina.tv, kartina.vod & videostreams", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=Ktv_api_start, icon="plugin.png")
	]

