import sys
from os import path, remove
import unittest
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from db import Db

class Test(unittest.TestCase):

	def tearDown(self):
		self._deleteDb('test.db')

	def _deleteDb(self, database):
		try:
			remove(database)

		except OSError:
			pass

	def test_init(self):
		self._deleteDb('test.db')
		db = Db('test.db')
		db = Db('test.db')

	def test_getNextDownload_empty_table(self):
		self._deleteDb('test.db')
		db = Db('test.db')

		self.assertIsNone(db.getNextDownload())













if __name__ == '__main__':
    unittest.main()