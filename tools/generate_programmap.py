import urllib2
import json
import yaml
import time
import logging
import argparse

__description__ = '''
'''

if __name__ == '__main__':
    
    p = argparse.ArgumentParser(description=__description__)
    p.add_argument('--logfile', help='logfile location')
    p.add_argument('--log2console', action='store_true', help='enables logging to console')
    p.add_argument('--loglevel', default='INFO', help='log level DEBUG|INFO|WARNING|ERROR|CRITICAL')

    args = vars(p.parse_args())
    
    ################################################################################
    # LOGGING
    ################################################################################   
    logging_format = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(message)s')
    
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

    current_time = time.time()
    days = []
    programmap = {}
    endReached = False

    while True:
        result = json.loads(urllib2.urlopen('https://audioapi.orf.at/oe1/api/json/current/broadcasts?_s=%s' % (current_time,)).read())
        for day in result:
            logging.info('scanning day %s', day['day'])
            if day['day'] in days: 
                endReached = True
            days.append(day['day'])
            for broadcast in day['broadcasts']:
                if broadcast['programTitle'] and not programmap.has_key(broadcast['program']):
                    logging.info('program %s: %s', broadcast['program'], broadcast['programTitle'])
                    programmap[str(broadcast['program'])] = broadcast['programTitle']
        if endReached:
            break
    
    with open('programmap.yaml', 'wb') as yamlfile:
        yaml.safe_dump(programmap, yamlfile, encoding='utf-8', default_flow_style=False, allow_unicode=True)
