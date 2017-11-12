import logging
import hashlib
import urllib2
import mutagen
import datetime
from sqlite3 import IntegrityError

class Download(object):

	def __init__(self,
		loopStreamId,		
		broadcastId,
		md5='',
		size=0,
		retries=0,
		status='downloading'
	):
		self.loopStreamId = loopStreamId
		self.broadcastId = broadcastId
		self.md5 = md5
		self.size = size
		self.retries = retries
		self.status = status


	def getHref(self):
		return 'http://loopstream01.apa.at/?channel=oe1&id=%s' % self.loopStreamId


	def setStatus(self, db, status):
		db.cursor.execute('UPDATE downloads SET status=? WHERE loopStreamId=?', (status, self.loopStreamId))
		self.status = status
		db.conn.commit()


	def save(self, db):
		now_iso = datetime.datetime.now().isoformat()
		try:
			db.cursor.execute('''
				INSERT INTO downloads VALUES (?, ?, ?, ?, ?, ?, ?, ?);
			''', (self.loopStreamId, self.broadcastId, self.md5, self.size, self.retries, self.status, now_iso, now_iso))
			db.conn.commit()
			return 'inserted'

		except IntegrityError:
			db.cursor.execute('''
				UPDATE downloads SET broadcastId=?, md5=?, size=?, retries=?, updated=? 
				WHERE loopStreamId=?;
			''', (self.broadcastId, self.md5, self.size, self.retries, now_iso, self.loopStreamId))
			db.conn.commit()
			return 'updated'


	def download(self, filename, callback=None):
		
		logging.info('downloading "%s" to "%s"', self.loopStreamId, filename)
		
		m = hashlib.md5()
		chunksize = 16 * 1024
		self.size = 0
		
		with open(filename, 'wb') as fo:

			response = urllib2.urlopen(self.getHref(), timeout=10)
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



