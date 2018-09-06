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
					broadcastDay TEXT,
					entity TEXT,
					program TEXT,
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
					retries INTEGER,
					updated TEXT,
					created TEXT
				);
				''')

		except sqlite3.OperationalError as e:
			logging.debug('table broadcasts could not be created')

		try:
			self.cursor.execute('''
				CREATE TABLE downloads (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					loopStreamId TEXT,
					broadcastId INTEGER,
					md5 TEXT,
					size INTEGER,
					length INTEGER,
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


	def getNextDownload(self, id=None):
		if id:
			self.cursor.execute('''
				UPDATE broadcasts
				SET status='claimed'
				WHERE id=?;
			''', (id,))

		else:

			self.cursor.execute('''
				UPDATE broadcasts
				SET status='claimed'
				WHERE id IN (
				  SELECT id FROM broadcasts 
				  WHERE (status='new' AND state='C') 
				  OR (status='error' AND retries < 8 AND DATETIME(download_started, '+' || (retries*retries*retries*retries) || ' minutes') < DATETIME('now', 'localtime'))
				  OR (status='downloading' AND DATETIME(download_started, '+60 minutes') < DATETIME('now', 'localtime'))
				  ORDER BY niceTime DESC
				  LIMIT 1
				);
			''')
		
		self.cursor.execute("SELECT * FROM broadcasts WHERE status='claimed' LIMIT 1")
		result = self.cursor.fetchone()
		
		if result:
			return Broadcast(*result)
			
	def getBroadcasts(self, limit=500):
		self.cursor.execute('''
			SELECT * FROM broadcasts
			where status='OK'
			ORDER BY start DESC
			LIMIT ?
		''', (limit, ))
		
		for broadcast in self.cursor.fetchall():
			yield Broadcast(*broadcast)
	
	def getBroadcastsByProgram(self, program, limit=50):
		self.cursor.execute('''
			SELECT * FROM broadcasts
			WHERE program=?
			AND status='OK'
			ORDER BY start DESC
			LIMIT ?
		''', (program, limit))
		
		for broadcast in self.cursor.fetchall():
			yield Broadcast(*broadcast)
	
	def getBroadcastsByRessort(self, ressort, limit=100):
		self.cursor.execute('''
			SELECT * FROM broadcasts
			WHERE ressort=?
			AND status='OK'
			ORDER BY start DESC
			LIMIT ?
		''', (ressort, limit))
		
		for broadcast in self.cursor.fetchall():
			yield Broadcast(*broadcast)
