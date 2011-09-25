# nitrogen14 - www.pristavka.de
# 
# Thanks to Eugene Bond
# kartina tv XML api

import urllib2
from xml.etree.cElementTree import fromstring
from time import time, localtime, strftime
from datetime import datetime, date, timedelta


KARTINA_API = 'http://iptv.kartina.tv/api/xml/%s'

class Kartina_Api:
	
	def __init__(self, login, password):
		self.SID = None
		self.channels = []
		self.watch_now_channels = []
		self.radio_channels = []
		self.groups = []
		self.channels_ttl = 0
		self.login = login
		self.password = password
		self.servertime = 0
		self.servertime_str = None
		self.servertime_date = None
		self.epg_time = 0
		self.epg = []
		self.epg_now = []
		self.packet_name = None
		self.packet_expire = None 
		self.time_show_now = 0
		self.epg_id = 0
		self.favorite_list = []
		self.favorite_chan_list = []
		self.nextday_epg_ut_start = None
		self.epg_next3 = []
		self.next_program = []
		self.all_vod_list = []
		self.total = 0
		self.page = 0
		self.nums = 0
		
	def _request(self, cmd, params):
		
		if self.SID == None:
			if cmd != 'login':
				self._auth(self.login, self.password)

		url = KARTINA_API % cmd
		url = url + '?' + params
		if (self.SID != None):
			url = url + '&' + self.SID
		try:
			req = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nKTV 0.4.9', 'Connection': 'Close'})
			xmlstream = urllib2.urlopen(req).read()
			res = fromstring(xmlstream)
		except Exception, ex:
			print ex
			res = fromstring('<error>no connection to host</error>')
			
		
		self._errors_check(res)

		if res.findtext('servertime'):	
			self.servertime = res.findtext('servertime')
			self.servertime_str = datetime.fromtimestamp(float(self.servertime)).strftime('%H:%M')
			self.servertime_date = datetime.fromtimestamp(float(self.servertime)).strftime('%d%m%y')
			
		return res
	
	def _auth(self, user, password):
		response = self._request('login', 'login=%i&pass=%i' % (user, password))
			
		if response.findtext('sid'):
			self.SID = '%s=%s' % (response.findtext('sid_name'), response.findtext('sid'))
		if response.findtext('account/packet_name'):	
			self.packet_name = response.findtext('account/packet_name')
		if response.findtext('account/packet_expire'):	
			self.packet_expire = response.findtext('account/packet_expire')


	def _errors_check(self, xml):
		if len(xml.findall('error')):
			print xml.findall('error')
			self.SID = None
			
			
	def vod_geturl(self, id=None):
		url = None
		try:
			xmlVodURL = self._request('vod_geturl', 'fileid=%s' % id)
			url = xmlVodURL.findtext('url')
			url = url.split(' ')[0]
		except:
			print 'vod_geturl error'
		return url
		
	def get_vod_list(self, req_type=None, page=None, query=None, genre=None, nums=None, mode=None ):
		vod_list = []
		try:
			xmlVodList = self._request('vod_list', 'type=%s&page=%s&query=%s&genre=%s&nums=%s' % (req_type, page, query, genre, nums))
			self.nums = int(nums)
			self.page = int(xmlVodList.findtext('page'))
			self.total = int(xmlVodList.findtext('total'))
			counter = int(nums)*(int(page)-1)



			for row in xmlVodList.findall('rows/item'):
				counter =  counter + 1
				counter_str = '%i' % counter
				if mode:
					counter_str = ''
				vod_tuple = (
					row.findtext('id'),
					row.findtext('dt_modify'),
					row.findtext('name').encode('utf-8'),
					row.findtext('name_orig').encode('utf-8'),
					row.findtext('description').encode('utf-8'),
					row.findtext('poster'),
					row.findtext('year'),
					row.findtext('rate_imdb'),
					row.findtext('rate_kinopoisk'),
					row.findtext('rate_mpaa'),
					row.findtext('country').encode('utf-8'),
					row.findtext('genre_str').encode('utf-8'),
					counter_str
				)
				vod_list.append(vod_tuple)
		except:
			print 'get_vod_list error'			
		return vod_list
		

	def get_vod_info(self,film_id):

		try:
			row = self._request('vod_info', 'id=%s' % film_id)
			videos = []
			for video in row.findall('film/videos/item'):
				video_tulpe = (
				video.findtext('id'),
				video.findtext('title')
				)
				videos.append(video_tulpe)
			
			vod_info = (
				row.findtext('film/name').encode('utf-8'),
				row.findtext('film/name_orig').encode('utf-8'),
				row.findtext('film/description').encode('utf-8'),
				row.findtext('film/lenght'),
				row.findtext('film/year'),
				row.findtext('film/genre_str').encode('utf-8'),
				row.findtext('film/director').encode('utf-8'),
				row.findtext('film/scenario').encode('utf-8'),
				row.findtext('film/actors').encode('utf-8'),
				videos,
				row.findtext('film/poster').encode('utf-8'),
			)
		except:
			print 'get_vod_info error'
			vod_info = ('','','','','','','','','',[])			
		
		return vod_info
		
	def get_genres(self):
		genres_list = []
		xmlGenList = self._request('vod_genres', '')
		for row in xmlGenList.findall('genres/item'):
			temp = (
				row.findtext('id'),
				row.findtext('name').encode('utf-8')
				)
			genres_list.append(temp)
		return genres_list 
		   
	def channel_list_refresch(self):
		self.channels_ttl = time()-1
		self.channel_list()
		
	def channel_list(self):
		if self.channels_ttl < time():
			xmlChannels = self._request('channel_list', '')
			self.channels = []
			self.watch_now_channels = []
			self.groups = []
			cat_nr = 0
			self.favorite_chan_list = []
			for idx in self.favorite_list:
				self.favorite_chan_list.append((''))
   
			fav_counter = 0
			chan_counter = 0
			group_counter = 0
			
			
			for group in xmlChannels.findall('groups/item'):
				
				
				group_number = group.findtext('id')
				if group_number:
					if group_number != "21":
						group_counter = group_counter + 1
				else:
					group_number = ""

				group_name = group.findtext('name')
				if not group_name:
					group_name = ""
   
				cat_channels = []
				id_group_counter = 0
				
				for channel in group.findall('channels/item'):
					chan_counter = chan_counter + 1
					
					programm = channel.findtext('epg_progname')
					id_group_counter = id_group_counter + 1

					prog = ""
					desc = ""
					duration = 0
					percent = 0
					
					is_time_to_watch = ""
					elapsed_time_min = 0 
					time_left_min = 0
					percent = 0

					if programm:
						programm = programm.split("\n",1)	
						if len(programm)>0:
							prog = programm[0]

						if len(programm)>1:	
							desc = programm[1]
   
					epg_start = channel.findtext('epg_start')
					if not epg_start:
						epg_start = ""
						epg_start_time = ""
					else:
						epg_start = int(epg_start)
						epg_start_time = datetime.fromtimestamp(float(epg_start)).strftime('%H:%M')

					epg_end = channel.findtext('epg_end')
					if not epg_end:
						epg_end = ""	
						epg_end_time = ""
					else:
						epg_end = int(epg_end)
						epg_end_time = datetime.fromtimestamp(float(epg_end)).strftime('%H:%M')
   
					if (epg_start!="" and epg_end!=""):
						now = int(self.servertime) 
						duration = (epg_end - epg_start)/60
						percent = int(epg_end - epg_start)/100
						time_left = int(epg_end - now)
						elapsed_time = int(now - epg_start)
						
						if percent!=0:
							percent = int(elapsed_time/percent)
						
						elapsed_time_min = int(elapsed_time/60)
						time_left_min = int(time_left/60)
						if ((elapsed_time_min < self.time_show_now) or (time_left_min < self.time_show_now)) and percent < self.time_show_now:
							is_time_to_watch = "yes"

					is_video = channel.findtext('is_video')
					idx = channel.findtext('id')

					for x in xrange(len(self.favorite_list)):
						if self.favorite_list[x] == idx:
							fav_counter = x+1
							break						
					
					channel_tuple = (
						idx,
						channel.findtext('name').encode('utf-8'),
						prog.encode('utf-8'),
						desc.encode('utf-8'),
						epg_start_time,
						epg_end_time,
						percent,
						elapsed_time_min,
						time_left_min,
						epg_end,
						duration,
						is_video,
						channel.findtext('have_archive'),
						channel.findtext('protected'),
						epg_start,
						chan_counter,
						id_group_counter,
						fav_counter,
						group_name.encode('utf-8'),
						group_counter
					)

					if is_video == '1':
						#self.radio_channels.append(channel_tuple)
					#else:
						if group_number != "21":
							self.channels.append(channel_tuple)
							if idx in self.favorite_list: 
								position = self.favorite_list.index(idx)
								self.favorite_chan_list[position] = channel_tuple
						cat_channels.append(channel_tuple)				
					
					if is_time_to_watch:
						self.watch_now_channels.append(channel_tuple)
				counter = len(cat_channels) 
				if 	group_number != "23": # RADIO
					cat_nr = cat_nr + 1 
					self.groups.append( ( 
						'%i' % cat_nr,
						group_name.encode('utf-8'),
						group_number,
						'%i' % counter,
						cat_channels		
						))
			
			self.channels_ttl = time() + 60
		
		return self.channels
	

	def getChannel_url(self, ch_id, gmt_time):
		url = None
		if (gmt_time!=0):
			params = 'cid=%s&gmt=%s&protect_code=%s' % (ch_id, gmt_time, self.password)
		else:
			params = 'cid=%s&protect_code=%s' % (ch_id, self.password)
		response = self._request('get_url', params)
		url = response.findtext('url')
		if url:
			url = url.split(' ')[0].replace('http/ts://', 'http://')
		
		return url		
		
		 
	def get_epg(self, id, day=None, channel=None):


		params = 'cid=%s&day=%s' % (id, day)
		xmlEpg = self._request('epg', params)
		
		self.epg = []

		index = -1    
		self.epg_id = index

		for epg in xmlEpg.findall('epg/item'):
			index = index +1 
			archive = False
			percent = 0

			ut_start = epg.findtext('ut_start')

			if channel:
				if channel[12]:
					archive = True

			if not ut_start:
				ut_start = ""
				ut_start_time = "" 
				ut_start_date = ""
			else:
				ut_start_time = datetime.fromtimestamp(float(ut_start)).strftime('%H:%M')
				ut_start_date = datetime.fromtimestamp(float(ut_start)).strftime('%d%m%y')
				if ut_start_date == self.servertime_date:
					ut_start_date = '%s' % datetime.fromtimestamp(float(ut_start)).strftime('%d-%m-%Y')
					ut_start_day = 'TODAY'
					if channel:
						if int(ut_start) == channel[14]:
							self.epg_id = index
							percent = channel[6]					
				else:
					ut_start_date = datetime.fromtimestamp(float(ut_start)).strftime('%d-%m-%Y')
					ut_start_day = datetime.fromtimestamp(float(ut_start)).strftime('%A')


			epg_prog = ""
			epg_desc = ""

			epg_progname = epg.findtext('progname')

			epg_programm = []
			if epg_progname:
				epg_programm = epg_progname.split("\n",1)	
				if len(epg_programm)>0:
					epg_prog = epg_programm[0].encode('utf-8')

				if len(epg_programm)>1:	
					epg_desc = epg_programm[1].encode('utf-8')


			self.epg.append( (
				ut_start,
				epg_prog,
				epg_desc,
				ut_start_time,
				ut_start_date,
				archive,
				percent,
				ut_start_day  
			))
			
		return self.epg

	def get_epg_next3(self, id):

		params = 'cid=%s' % (id)
		print params
		xmlEpg = self._request('epg_next', params)
		self.epg_next3 = []

		for epg in xmlEpg.findall('epg/item'):
			epg_prog = ""
			epg_desc = ""
			ts = epg.findtext('ts')
			if not ts:
				return ('','','','')

			epg_progname = epg.findtext('progname')

			epg_programm = []
			if epg_progname:
				epg_programm = epg_progname.split("\n",1)	
				if len(epg_programm)>0:
					epg_prog = epg_programm[0].encode('utf-8')

				if len(epg_programm)>1:	
					epg_desc = epg_programm[1].encode('utf-8')  
			
			self.epg_next3.append( (
				int(ts),
				epg_prog,
				epg_desc  
			))
		try:   
			duration = int((self.epg_next3[2][0]-self.epg_next3[1][0])/60)
			start = datetime.fromtimestamp(float(self.epg_next3[0][0])).strftime('%H:%M')
			end = datetime.fromtimestamp(float(self.epg_next3[1][0])).strftime('%H:%M')
			self.next_program = (self.epg_next3[1][1], self.epg_next3[1][2], duration, start, end )
		except:
			return ('','','','')
			
		return self.next_program 
		

	def get_epg_first_time(self, id, day=None):
		params = 'cid=%s&day=%s' % (id, day)
		xmlEpgNext = self._request('epg', params)   
		nextday_epg = xmlEpgNext.findall('epg/item')
		try:
			self.nextday_epg_ut_start = nextday_epg[0].findtext('ut_start')
		except:
			self.nextday_epg_ut_start = self.servertime_str    