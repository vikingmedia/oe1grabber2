import logging
import hashlib
import urllib.request, urllib.error, urllib.parse
import datetime
from sqlite3 import IntegrityError
from mutagen.mp3 import MP3


class Download(object):

	def __init__(self,
		id,
		loopStreamId,
		broadcastId,
		md5='',
		length=0,
		size=0,
		retries=0,
		status='downloading'
	):
		self.id = id
		self.loopStreamId = loopStreamId
		self.broadcastId = broadcastId
		self.md5 = md5
		self.length = length
		self.size = size
		self.status = status


	def getHref(self):
		return 'https://loopstream01.apa.at/?channel=oe1&id=%s' % self.loopStreamId


	def save(self, db):
		now_iso = datetime.datetime.now().isoformat()
		if self.id != None:
			db.cursor.execute('''
				UPDATE downloads SET broadcastId=?, md5=?, length=?, size=?, updated=?, loopStreamId=?, status=?
				WHERE id=?;
			''', (self.broadcastId, self.md5, self.size, self.length, now_iso, self.loopStreamId, self.status, self.id))
			db.conn.commit()
			return 'updated'

		else:
			db.cursor.execute('''
				INSERT INTO downloads
				(loopStreamId, broadcastId, md5, length, size, status, updated, created)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?);
			''', (self.loopStreamId, self.broadcastId, self.md5, self.length, self.size, self.status, now_iso, now_iso))
			db.conn.commit()
			self.id = db.cursor.lastrowid
			return 'inserted'


	def download(self, filename, callback=None):

		logging.info('downloading "%s" to "%s"', self.loopStreamId, filename)

		m = hashlib.md5()
		chunksize = 16 * 1024
		self.size = 0

		url = self.getHref()
		logging.debug('GET %s', url)

		with open(filename, 'wb') as fo:

			response = urllib.request.urlopen(url, timeout=10)
			contentLength = int(response.headers['content-length'])

			while True:
				chunk = response.read(chunksize) #socket.timeout: timed out

				if not chunk:
					break

				self.size += len(chunk)
				m.update(chunk)
				fo.write(chunk)

				if callback:
					callback(contentLength, self.size)

		self.md5 = m.hexdigest()
		mp3info = MP3(filename).info
		self.length = mp3info.length

	def getLength(self):
		return self.length
