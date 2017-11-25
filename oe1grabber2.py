import urllib2
import json
import logging
import time
from day import Day
from broadcast import Broadcast
from db import Db
from download import Download
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from progressbar import progressBarCallback
from socket import timeout
import argparse
import os

__description__ = '''
'''
logging_format = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(message)s')

if __name__ == '__main__':

    p = argparse.ArgumentParser(description=__description__)
    p.add_argument('--output', help='output directory', default='')
    p.add_argument('--id', help='download a certain broadcast id, e.g. 44928')
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

    while True:

        now = time.time()
        if current_time + 2.5*60 < now:
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

            filename = os.path.join(outdir, broadcast.getFileName(max_length=100))
            error = False
            
            for loopStreamId in broadcast.getloopStreamIds():
                
                download = Download(loopStreamId, broadcast.id)
                download.save(db)   

                try:
                    download.download(filename, progressBarCallback)
                    download.save(db)
                    print

                except urllib2.URLError, timeout:
                    download.retries += 1
                    download.save(db)
                    download.setStatus(db, 'error')
                    broadcast.setStatus(db, 'error')
                    error = True
                    continue
                
                download.setStatus(db, 'OK')

                target_length = broadcast.getLength()
                logging.info('target length: %s', target_length)
                mp3info = MP3(filename).info
                length = mp3info.length
                logging.info('length = %s', length)
                delta_length = length - target_length
                logging.info('delta length = %s', delta_length)
                #if abs(delta_length) > 60
                #logging.info('length: %s', info.length)
                #logging.info('blength: %s', broadcast.getLength())
                #logging.info(str(int((broadcast.getLength() / info.length) * 100)) + ' %')

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
                tags.save(filename)
                broadcast.setStatus(db, 'OK')

        except KeyboardInterrupt:
            broadcast.setStatus(db, 'error')
            break

        except:
            logging.exception('')

        if id:
            break  #if id parameter was give, stop at this point