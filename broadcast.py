import datetime
from sqlite3 import IntegrityError
import json
import urllib2
from dateutil.parser import parse
import re
from rfeed import *

class Broadcast(object):

	def __init__(self, 
			id,
			href,
			station,
			entity,
			program,
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
			retries=0,
			updated='',
			created=''
		):
		self.href = href
		self.station = station
		self.entity = entity
		self.id = id
		self.program = program
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
		self.retries = retries
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
		return re.sub('\s+', ' ', (('['+self.programTitle+'] - ') if self.programTitle else '')+self.title)

	def getFileName(self, max_length=100):
		return re.sub('[\?\/]', '', (self.niceTime[:10]+' '+self.niceTime[11:19] \
			+' - [{0:02d}] '.format(self.tracknumber)+self.getTitle())[:max_length-4]+'.mp3')

	def getLength(self):
		return (parse(self.end) - parse(self.start)).total_seconds()


	def setStatus(self, db, status):
		db.cursor.execute('''
			UPDATE broadcasts SET status=?, updated=? 
			WHERE id=?''', (status, datetime.datetime.now().isoformat(), self.id))
		self.status = status
		db.conn.commit()


	def setDownloadStarted(self, db, starttime):
		db.cursor.execute('''
			UPDATE broadcasts SET download_started=?, updated=DATETIME('now', 'localtime') 
			WHERE id=?''', (starttime.isoformat(), self.id))
		self.download_started = starttime.isoformat()
		db.conn.commit()


	def incrementRetries(self, db):
		db.cursor.execute('''
			UPDATE broadcasts SET retries=retries+1, updated=DATETIME('now', 'localtime') 
			WHERE id=?''', (self.id, ))
		db.conn.commit()
		self.retries += 1		


	def save(self, db):
		now_iso = datetime.datetime.now().isoformat()
		try:
			db.cursor.execute('''
				INSERT INTO broadcasts VALUES (
					?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
				);
				''', (
					self.id,
					self.href,
					self.station,
					self.entity,
					self.program,
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
					self.retries,
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
					program=?,
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
					self.program,
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
			
	def getWebLink(self):
		'''
		https://oe1.orf.at/programm/20180903/526094
		'''
		return 'https://oe1.orf.at/programm/{broadcastDay}/{programKey}' \
		.format(
			broadcastDay=self.broadcastDay, 
			programKey=self.programKey
		)
		
	def getFeedItem(self,
			enclosureUrl,
			enclosureLength,
			enclosureType
		):
		return Item(
			title = self.getTitle(),
			link = self.getWebLink(),
			description = self.subtitle,
			guid = Guid(self.getWebLink()),
			pubDate = parse(self.niceTime),
			enclosure = Enclosure(
				url = enclosureUrl,
				length = enclosureLength,
				type = enclosureType
			)
		)

	def __str__(self):
		return self.getFileName()
