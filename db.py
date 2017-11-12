import sqlite3
import logging
from broadcast import Broadcast

class Db(object):

	def __init__(self, database):
		self.conn = sqlite3.connect(database)
		self.cursor = self.conn.cursor()
		self._createTables()

	def _createTables(self):
		try:
			self.cursor.execute('''
				CREATE TABLE broadcasts (
					id INTEGER PRIMARY KEY,
					href TEXT,
					station TEXT,
					entity TEXT,
					programKey TEXT,
					programTitle TEXT,
					title TEXT,
					subtitle TEXT,
					ressort TEXT,
					state TEXT,
					isOnDemand INTEGER,
					isGeoProtected INTEGER,
					start TEXT,
					end TEXT,
					scheduledStart TEXT,
					scheduledEnd TEXT,
					niceTime TEXT,
					status TEXT,
					tracknumber INTEGER,
					download_started TEXT,
					updated TEXT,
					created TEXT
				);
				''')

		except sqlite3.OperationalError as e:
			logging.debug('table broadcasts could not be created')

		try:
			self.cursor.execute('''
				CREATE TABLE downloads (
					loopStreamId TEXT PRIMARY KEY,
					broadcastId INTEGER,
					md5 TEXT,
					size INTEGER,
					retries INTEGER,
					status TEXT,
					updated TEXT,
					created TEXT
				);
				''')
		except sqlite3.OperationalError:
			logging.debug('table downloads could not be created')

		try:
			self.cursor.execute('CREATE INDEX broadcasts_state_index ON broadcasts (state);')

		except sqlite3.OperationalError:
			logging.debug('index broadcasts_state_index could not be created')

		self.conn.commit()


	def getNextDownload(self):
		self.cursor.execute('''
			UPDATE broadcasts
			SET status='claimed'
			WHERE (status='new' AND state='C') 
			OR (status='error' AND DATETIME(created, '+12 hours') > DATETIME('now'))
			OR (status='downloading' and DATETIME(download_started, '+1 hour') < DATETIME('now'))
			ORDER BY niceTime DESC
			LIMIT 1;
		''')
		
		self.cursor.execute("SELECT * FROM broadcasts WHERE status='claimed' LIMIT 1")
		result = self.cursor.fetchone()
		
		if result:
			broadcast = Broadcast(*result)
			broadcast.setStatus(self, 'dowloading')
			return broadcast
