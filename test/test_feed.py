#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
from os import path, remove
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
sys.dont_write_bytecode = True
import copy

from feed import Feed
from broadcast import Broadcast
import yaml

class Test(unittest.TestCase):
    
    def setUp(self):
        self.broadcast = Broadcast(
            href='https://audioapi.orf.at/oe1/api/json/current/broadcast/524214/20180829',
            station='oe1',
            broadcastDay=20180829,
            entity='Broadcast',
            id=61325,
            program='24',
            programKey='524214',
            programTitle='Ausgewählt'.decode('utf-8'),
            title='Kirchen verurteilen Vorfälle in Chemnitz'.decode('utf-8'),
            subtitle='<p>Was die junge arabische Community denkt, fühlt und bewegt +++ Kirchen verurteilen Vorfälle in Chemnitz. - Moderation: Markus Veinfurter</p>'.decode('utf-8'),
            ressort='religion',
            state='C',
            isOnDemand=True,
            isGeoProtected=False,
            start='2018-08-29T18:55:00+02:00',
            end='2018-08-29T18:59:59+02:00',
            scheduledStart='2018-08-29T18:55:00+02:00',
            scheduledEnd='2018-08-29T19:00:00+02:00',
            niceTime='2018-08-29T18:55:00+02:00',
            tracknumber=1
        )
           
    def test_explicitTitle(self):
        feed = Feed(
            'http://localhost', 
            'Müller'.decode('utf-8'), 
            'Müller.rss'.decode('utf-8'), 
            'Mähdrescher'.decode('utf-8')
        )
        feed.addItem(self.broadcast)
        self.assertEqual(feed.title.encode('utf-8'), 'Müller')

    def test_explicitFilename(self):
        feed = Feed(
            'http://localhost', 
            'Müller'.decode('utf-8'), 
            'Müller.rss'.decode('utf-8'), 
            'Mähdrescher'.decode('utf-8')
        )
        feed.addItem(self.broadcast)
        self.assertEqual(feed.filename.encode('utf-8'), 'Müller.rss')
        
    def test_rss(self):
        feed = Feed('http://localhost', 'a', 'b')
        feed.addItem(self.broadcast)
        feed.rss()
    
    def test_save(self):
        feed = Feed(
            'http://localhost', 
            'Müller'.decode('utf-8'), 
            'Müller.rss'.decode('utf-8'), 
            'Mähdrescher'.decode('utf-8')
        )
        feed.addItem(self.broadcast)
        self.assertEqual(feed.subdir.encode('utf-8'), 'Mähdrescher')
        feed.save('/tmp')
        
    def test_yaml(self):
        programmap = yaml.load("""
            "3": Die Ö1 Klassiknacht
            """
        )
        feed = Feed(
            baseUrl = 'http://localhost', 
            title = programmap.get('3', 'Programm Nr. 3'), 
            filename = programmap.get('3', 'Programm Nr. 3') + '.rss', 
            subdir = 'Programme'
        )
        feed.addItem(self.broadcast)
        self.assertEqual(feed.filename.encode('utf-8'), 'Die Ö1 Klassiknacht.rss')
        
    
        
if __name__ == '__main__':
    unittest.main()

