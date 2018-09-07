import rfeed
import datetime
import urllib
import os

class Feed(object):
    
    def __init__(self, 
        baseUrl, 
        title, 
        filename, 
        subdir=''
        ):
        self.items = []
        self.baseUrl = baseUrl
        self.title = title
        self.filename = filename
        self.subdir = subdir
        
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
                
        
    def rss(self):
        link = '/'.join(
            filter(None,[
                self.baseUrl, 
                'rss',
                urllib.quote(self.subdir.encode('utf-8')),
                urllib.quote(self.filename.encode('utf-8'))]
            )
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
        path = os.path.join(*filter(None, [output, self.subdir]))
        rssdir = os.path.join(output, 'rss')
        
        try:
            os.makedirs(path)

        except OSError:
            pass

        with open(os.path.join(path, self.filename), 'wb') as rssfile:
            rssfile.write(self.rss())
        

