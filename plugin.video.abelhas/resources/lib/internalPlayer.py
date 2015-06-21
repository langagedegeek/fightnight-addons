# -*- coding: utf-8 -*-

""" abelhas.pt
    2015 fightnight"""

import xbmc,xbmcaddon,xbmcgui,os,xbmcvfs,re

addon_id = 'plugin.video.abelhas'
selfAddon = xbmcaddon.Addon(id=addon_id)
datapath = xbmc.translatePath(selfAddon.getSetting('resumefolder'))
track = selfAddon.getSetting('track-player')

class Player(xbmc.Player):
	def __init__(self,title):
		xbmc.Player.__init__(self)
		print title

		self.dbid = xbmc.getInfoLabel('ListItem.DBID')
		tv = xbmc.getInfoLabel('ListItem.Art(tvshow.poster)')
		if tv == "": self.vidcontent = 'movie'
		else: self.vidcontent = 'episode'

		try: self.title=re.sub('[^-a-zA-Z0-9_\.()\\\/ ]+', ' ',  re.compile("\[COLOR .+?\](.+?)\[/COLOR\]").findall(title)[0])
		except: self.title=re.sub('[^-a-zA-Z0-9_\.()\\\/ ]+', ' ',  title)
		self.playing = True
		self.time = 0
		self.totalTime = 0
		if track == 'true':
			try: self.id = self.title
			except: self.id = None
			if not xbmcvfs.exists(datapath): xbmcvfs.mkdir(datapath)
			if self.id: self.filemedia = os.path.join(datapath,str(self.id)+'.txt')
			else: self.filemedia = None

	def onPlayBackStarted(self):
		try:
			self.totalTime = self.getTotalTime()
			print 'total time',self.totalTime
			if track == 'true' and self.isPlayingVideo():
				if xbmcvfs.exists(self.filemedia):
					print "Resume point available..."
					tracker=readfile(self.filemedia)
					opcao=xbmcgui.Dialog().yesno("Abelhas", 'Resume point available.','Continue from '+ ' %s?' % (format_time(float(tracker))),'', 'No', 'Yes')
					if opcao: self.seekTime(float(tracker))
		except: pass

	def onPlayBackStopped(self):
		print 'player Stop'
		self.playing = False
		time = int(self.time)
		print 'self.time/self.totalTime='+str(self.time/self.totalTime)
		if (self.time/self.totalTime > 0.90):
			self.onPlayBackEnded()
			if track == 'true' and self.isPlayingVideo():
				try: xbmcvfs.delete(self.filemedia)
				except: pass

	def onPlayBackEnded(self):
		if str(self.vidcontent) == 'episode':
			print "Marking Episode as watched"
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.dbid))
		elif str(self.vidcontent) == 'movie':
			print "Marking Movie as watched"
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.dbid))
		xbmc.executebuiltin('Container.Refresh')

	def track_time(self):
		try:
			if track == 'true' and self.isPlayingVideo():
				self.time = self.getTime()
				save(self.filemedia,str(self.time))
		except: pass

def save(filename, contents):
	try:
		fh = xbmcvfs.File(filename, 'w')
		fh.write(str(contents))
		fh.close()
	except: print "Nao gravou os temporarios de: %s" % (filename)

def readfile(filename):
    try:
		fh = xbmcvfs.File(filename)
		string = fh.read()
		fh.close()
		return string
    except:
		traceback.print_exc()
		print "Nao abriu conteudos de: %s" % filename
		return None

def format_time(seconds):
    minutes,seconds = divmod(seconds, 60)
    if minutes > 60:
        hours,minutes = divmod(minutes, 60)
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    else: return "%02d:%02d" % (minutes, seconds)