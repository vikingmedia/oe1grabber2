import rfeed
import datetime
import urllib
import os

class Feed(object):
    
    def __init__(self, baseUrl, title=None, filename=None):
        self.items = []
        self.baseUrl = baseUrl
        self.title = title
        self.filename = filename
        
    def addItem(self, broadcast):
        self.items.append(
            broadcast.getFeedItem(
                enclosureUrl = '/'.join([
                    self.baseUrl, 
                    'mp3',
                    urllib.quote(broadcast.getDirectoryName()), 
                    urllib.quote(broadcast.getFileName(max_length=100).encode('utf-8'))
                    ]
                ),
                enclosureLength = broadcast.getLength(),
                enclosureType = 'audio/mpeg'
            )
        )
        
        # set the feed title to the first the programTitle as default
        if not self.title and broadcast.getProgramTitle(): 
            self.title = u"\xd61 - "  + broadcast.getProgramTitle()
            
        # set the feed filename to the first the programTitle as default
        if not self.filename and broadcast.getProgramTitle(): 
            self.filename = broadcast.getProgramTitle() + '.rss'
        
        
    def rss(self):
        link = '/'.join([
            self.baseUrl, 
            'rss',
            urllib.quote(self.filename)]
        )
        
        return rfeed.Feed(
            title = self.title,
            link = link,
            description = self.title,
            language = "de-AT",
            lastBuildDate = datetime.datetime.now(),
            image = rfeed.Image(
                url = '/'.join([
                    self.baseUrl,
                    'images',
                    'default.png']
                ),
                title = self.title,
                link = link
            ),
            items = self.items
        ).rss()
        
        
    def save(self, output):
        with open(os.path.join(output, self.filename), 'wb') as rssfile:
            rssfile.write(self.rss())
        

