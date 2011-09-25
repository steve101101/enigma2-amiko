#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Modified by schpuntik
from xml.etree.ElementTree import fromstring, ElementTree, XML
import os

class iptv_streams:
	
	def __init__(self):
		self.iptv_list = []
		self.groups = []



	def readfile(self):
		myfile = open("/usr/lib/enigma2/python/Plugins/Extensions/nKTVplayer/moetv.m3u", "r")
		temp = []
		cat_channels = []
		group_name = 'MOE TB'
		picon = 'ovm.png'
		group_id = 1
		ts_stream = '1'
		stream_buffer = ''
		
		for line in myfile.readlines():  
			new_line = line[:-1]
			x = new_line.find(' ')
			if x>-1:
				new_line = new_line[x+1:]
			if new_line.strip() != '#EXTM3U':
				temp.append(new_line)

		chan_counter = 0

		for k in range(0, len(temp), 2):
			chan_counter = chan_counter +1

			chan_tulpe = (
				chan_counter,
				temp[k],
				picon,
				temp[k+1],
				ts_stream,
				stream_buffer,
				group_id,
				group_name
			)
			self.iptv_list.append(chan_tulpe)
			cat_channels.append(chan_tulpe)

		counter = len(self.iptv_list)
		
		self.groups.append((
			group_id,
			group_name,
			counter,
			cat_channels
			))

	def get_list(self):

		tree = ElementTree()
		tree.parse("/usr/lib/enigma2/python/Plugins/Extensions/nKTVplayer/nstream.xml")
		group_id = len(self.groups)
		chan_counter = len(self.iptv_list)
		for group in tree.findall('group'):
			group_id = group_id + 1
			group_name = ''
			group_name = group.findtext('name')
			group_name = group_name.encode('utf-8')
			cat_channels = []
			chan_id = 0
			for channel in group.findall('channel'):		
				chan_counter = chan_counter + 1 
				name = channel.findtext('name')
				name = name.encode('utf-8')
				piconname = channel.findtext('piconname')
				stream_url = channel.findtext('stream_url')
				ts_stream = channel.findtext('ts_stream')
				buffer_kb = channel.findtext('buffer_kb')

				chan_tulpe = (
					chan_counter,
					name,
					piconname,
					stream_url,
					ts_stream,
					buffer_kb,
					group_id,
					group_name,
				)
				self.iptv_list.append(chan_tulpe)
				cat_channels.append(chan_tulpe)
			counter = len(cat_channels)
			self.groups.append((
				group_id,
				group_name,
				counter,
				cat_channels
				))