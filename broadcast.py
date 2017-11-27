import datetime
from sqlite3 import IntegrityError
import json
import urllib2
from dateutil.parser import parse
import re

class Broadcast(object):

	def __init__(self, 
			id,
			href,
			station,
			entity,
			programKey,
			programTitle,
			title,
			subtitle,
			ressort,
			state,
			isOnDemand,
			isGeoProtected,
			start,
			end,
			scheduledStart,
			scheduledEnd,
			niceTime,
			status='new',
			tracknumber=1,
			download_started=None,
			updated='',
			created=''
		):
		self.href = href
		self.station = station
		self.entity = entity
		self.id = id
		self.programKey = programKey
		self.programTitle = programTitle
		self.title = title
		self.subtitle = subtitle
		self.ressort = ressort
		self.state = state
		self.isOnDemand = isOnDemand
		self.isGeoProtected = isGeoProtected
		self.start = start
		self.end = end
		self.scheduledStart = scheduledStart
		self.scheduledEnd = scheduledEnd
		self.niceTime = niceTime
		self.status = status
		self.tracknumber = tracknumber
		self.download_started = download_started
		self.updated = updated
		self.created = created


	def getDirectoryName(self):
		return parse(self.niceTime).strftime('%Y-%m-%d [%a]')

	def getGenre(self):
		return self.ressort if self.ressort else ''

	def getTracknumber(self):
		return str(self.tracknumber)

	def getAlbum(self):
		return parse(self.niceTime).strftime('%a, %d.%m.%Y')

	def getTitle(self):
		return (('['+self.programTitle+'] - ') if self.programTitle else '')+self.title

	def getFileName(self, max_length=100):
		return re.sub('[\?\/]', '', (self.niceTime[:10]+' '+self.niceTime[11:19] \
			+' - '+self.getTitle())[:max_length-4]+'.mp3')

	def getLength(self):
		return (parse(self.end) - parse(self.start)).total_seconds()


	def setStatus(self, db, status):
		db.cursor.execute('''
			UPDATE broadcasts SET status=?, download_started=datetime('now') 
			WHERE id=?''', (status, self.id))
		self.status = status
		db.conn.commit()


	def save(self, db):
		now_iso = datetime.datetime.now().isoformat()
		try:
			db.cursor.execute('''
				INSERT INTO broadcasts VALUES (
					?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
				);
				''', (
					self.id,
					self.href,
					self.station,
					self.entity,
					self.programKey,
					self.programTitle,
					self.title,
					self.subtitle,
					self.ressort,
					self.state,
					self.isOnDemand,
					self.isGeoProtected,
					self.start,
					self.end,
					self.scheduledStart,
					self.scheduledEnd,
					self.niceTime,
					self.status,
					self.tracknumber,
					self.download_started,
					now_iso,
					now_iso
				)
			)
			db.conn.commit()
			return 'inserted'

		except IntegrityError:
			db.cursor.execute('''
				UPDATE broadcasts SET 
					href=?, 
					station=?, 
					entity=?, 
					programKey=?, 
					programTitle=?,
					title=?,
					subtitle=?,
					ressort=?,
					state=?,
					isOnDemand=?,
					isGeoProtected=?,
					start=?,
					end=?,
					scheduledStart=?,
					scheduledEnd=?,
					niceTime=?,
					updated=?
				WHERE id=?; 			
				''', (
					self.href,
					self.station,
					self.entity,
					self.programKey,
					self.programTitle,
					self.title,
					self.subtitle,
					self.ressort,
					self.state,
					self.isOnDemand,
					self.isGeoProtected,
					self.start,
					self.end,
					self.scheduledStart,
					self.scheduledEnd,
					self.niceTime,
					now_iso,
					self.id
				)
			)
			db.conn.commit()
			return 'updated'

	def getloopStreamIds(self):
		try:
			result = json.loads(urllib2.urlopen(self.href).read())['streams']
		except urllib2.HTTPError:
			result = []
		for stream in result:
			yield stream['loopStreamId']

	def __str__(self):
		return self.getFileName()
