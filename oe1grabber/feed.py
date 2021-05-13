import rfeed
import datetime
import urllib.request, urllib.parse, urllib.error
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
                    urllib.parse.quote(broadcast.getDirectoryName()),
                    urllib.parse.quote(broadcast.getFileName(max_length=100).encode('utf-8'))
                    ]
                ),
                enclosureLength = broadcast.getLength(),
                enclosureType = 'audio/mpeg'
            )
        )


    def rss(self):
        link = '/'.join(
            [_f for _f in [
                self.baseUrl,
                'rss',
                urllib.parse.quote(self.subdir.encode('utf-8')),
                urllib.parse.quote(self.filename.encode('utf-8'))] if _f]
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
        path = os.path.join(*[_f for _f in [output, self.subdir] if _f])
        rssdir = os.path.join(output, 'rss')

        try:
            os.makedirs(path)

        except OSError:
            pass

        with open(os.path.join(path, self.filename), 'w') as rssfile:
            rssfile.write(self.rss())
