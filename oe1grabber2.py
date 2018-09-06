import urllib2
import urlparse
import urllib
import json
import logging
import time
from day import Day
from broadcast import Broadcast
from db import Db
from download import Download
from progressbar import progressBarCallback
from socket import timeout
import argparse
import os
import datetime
import tempfile
from mutagen.easyid3 import EasyID3

from rfeed import Feed

__description__ = '''
'''
logging_format = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(message)s')

if __name__ == '__main__':

    p = argparse.ArgumentParser(description=__description__)
    p.add_argument('--output', help='output directory', default='')
    p.add_argument('--baseurl', help='base URL for RSS feeds', default='http://localhost')
    p.add_argument('--id', help='download a certain broadcast id, e.g. 44928')
    p.add_argument('--timelimit', default=2.5, type=float, help='run only for a limited amount of time[%(default)s minutes]')
    p.add_argument('--logfile', help='logfile location')
    p.add_argument('--log2console', action='store_true', help='enables logging to console')
    p.add_argument('--loglevel', default='INFO', help='log level DEBUG|INFO|WARNING|ERROR|CRITICAL')

    args = vars(p.parse_args())
    
    ################################################################################
    # LOGGING
    ################################################################################   
    
    logger = logging.getLogger()
    log_level = eval('logging.%s' % args['loglevel'])
    logger.setLevel(log_level)        
    
    if args['logfile']:
        fh = logging.FileHandler(args['logfile'])
        fh.setLevel(log_level)
        fh.setFormatter(logging_format)
        logger.addHandler(fh)
        
    if args['log2console']:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(logging_format)
        logger.addHandler(ch)
        
    if len(logger.handlers) == 0:
        logger.addHandler(logging.NullHandler())

    # set up
    db = Db('oe1grabber2.db')

    # try to download
    current_time = int(time.time())

    logging.info('current time is %s', current_time)

    # update broadcast db
    result = json.loads(urllib2.urlopen('https://audioapi.orf.at/oe1/api/json/current/broadcasts?_s=%s' % (current_time,)).read())
    for d in result:
        day = Day(d)
        for broadcast in day.broadcasts:
            if broadcast.save(db) == 'inserted':
                logging.info('inserted new broadcast: %s', broadcast)
                
    programs = {}
    ressorts = {}

    while True:

        now = time.time()
        if current_time + args['timelimit']*60 < now:
            logging.info('stopped after %s seconds', now-current_time)
            break

        try:

            broadcast = db.getNextDownload(id=args['id'])

            if not broadcast:
                logging.info('nothing to download')
                break
        
            outdir = os.path.join(args['output'], broadcast.getDirectoryName())

            try:
                os.makedirs(outdir)

            except OSError:
                logging.debug('directory "%s" could not be created', outdir)

            tmpfilelocation = os.path.join(tempfile.gettempdir(), broadcast.getFileName(max_length=100))
            error = False
            
            # technically multiple streams are possible, but as for now
            # only one stream is associated with a broadcast
            for loopStreamId in broadcast.getloopStreamIds():
                
                broadcast.setStatus(db, 'downloading')
                broadcast.setDownloadStarted(db, datetime.datetime.now())
                download = Download(None, loopStreamId, broadcast.id)
                download.save(db)   

                try:
                    download.download(tmpfilelocation, progressBarCallback)
                    print
                    logging.info('download hash for "%s" was %s', 
                        download.broadcastId, download.md5)
                    
                except urllib2.URLError, timeout:
                    download.status = 'URLError or timeout'
                    download.save(db)
                    error = True
                    continue

                target_length = broadcast.getLength()
                length = download.getLength()
                logging.info('target length: %s', target_length)
                logging.info('length: %s', length)
                delta_length = length - target_length
                delta_length_percent = (delta_length / target_length) * 100
                msg = 'delta length: %4.2fs [%4.2f%%]' % (delta_length, delta_length_percent)
                logging.info(msg)
                if delta_length_percent < -25:
                    broadcast.incrementRetries(db)
                    error = True
                    download.status = 'error: ' + msg
                    download.save(db)
                    try: 
                        logging.info('deleting temporary file "%s"', tmpfilelocation)
                        os.remove(tmpfilelocation)
                    except OSError:
                        pass
                    
                else:
                    download.status = msg
                    download.save(db)

            if error:
                broadcast.setStatus(db, 'error')
            else:
                logging.info('adding ID3 tags')
                tags = EasyID3()
                tags['title'] = broadcast.getTitle()
                tags['album'] = broadcast.getAlbum()
                tags['tracknumber'] = broadcast.getTracknumber()
                tags['genre'] = broadcast.getGenre()
                tags['artist'] = u'\xd61'
                tags.save(tmpfilelocation)
                broadcast.setStatus(db, 'OK')

                programs[broadcast.getProgram()] = True
                ressorts[broadcast.getRessort()] = True

                filelocation = os.path.join(outdir, broadcast.getFileName(max_length=100))
                logging.info('moving "%s" to "%s"', tmpfilelocation, filelocation)
                os.rename(tmpfilelocation, filelocation)

        except KeyboardInterrupt:
            broadcast.setStatus(db, 'error')
            break

        except:
            logging.exception('')

        if args['id']:
            break  #if id parameter was give, stop at this point
    
    # generate feeds for:
    # * all
    # * days
    # * programs
    # * ressorts
    for program in programs.keys():
        logging.info('generating feed for program "%s"', program)
        
        items = []
        for broadcast in db.getBroadcastsByProgram(program):
            logging.debug('  [+] %s', broadcast)
            items.append(
                broadcast.getFeedItem(
                    enclosureUrl = '/'.join([
                        args['baseurl'], 
                        urllib.quote(broadcast.getDirectoryName()), 
                        urllib.quote(broadcast.getFileName(max_length=100).encode('utf-8'))
                        ]
                    ),
                    enclosureLength = broadcast.getLength(),
                    enclosureType = 'audio/mpeg'
                )
            )
                      
        feed = Feed(
            title = u"\xd61 - "  + broadcast.getProgramTitle(),
            link = urlparse.urljoin(args['baseurl'], urllib.quote(broadcast.getProgramTitle().encode('utf-8')+'.rss')),
            description = u"\xd61 - " + broadcast.getProgramTitle(),
            language = "de-AT",
            lastBuildDate = datetime.datetime.now(),
            items = items
        )
        
        rss = feed.rss()
        with open(os.path.join(args['output'],'%s.rss' % (broadcast.getProgramTitle(),)), 'wb') as rssfile:
            rssfile.write(rss)
        
    for ressort in ressorts.keys():
        if not ressort:
            continue
        logging.info('generating feed for ressort "%s"', ressort)
        for broadcast in db.getBroadcastsByRessort(ressort):
            logging.debug('  [+] %s', broadcast)
        

