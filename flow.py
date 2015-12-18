import logging
import requests
import pickle
import os.path
import json
import re
import sys
import subprocess

from io import StringIO
from datetime import timedelta

class Flow:    
    format = '%d.%m.%Y'
    zip = False # zipped downloads not yet implemented

    def __init__(self, logger = None, period = 2, file = 'flow-session.dat', jsondir = 'json', datadir = 'data', persist = True, restart = False):
        self.logger = logger or logging.getLogger(__name__)
        self.jsondir = jsondir
        self.datadir = datadir
        if not os.path.exists(jsondir):
            os.makedirs(jsondir)

        self.period = 2 # weeks        
        self.file = file
        self.persist = persist
        self.restart = restart
        if not restart and persist and os.path.exists(file):
            self.logger.info('Reading session from file')
            file = open(self.file, 'rb')
            session_dump = file.read()
            self.session = pickle.loads(session_dump)
            file.close()
        else:
            self.session = requests.Session()
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.persist:
            self.logger.info('Writing session to file')
            session_dump = pickle.dumps(self.session)
            file = open(self.file, 'wb')
            file.write(session_dump)
            file.close()

    def isLoggedIn(self):
        self.logger.info('Checking login status')
        result = self.session.get('https://flow.polar.com/training/')
        return result.status_code is 200

    def login(self, email, password):
        if not self.restart and self.isLoggedIn():
            self.logger.info('Skip login')
            return True
        self.logger.info('Logging in')
        result = self.session.post(
            'https://flow.polar.com/login',
            data = {
                'email' : email,
                'password' : password
            },
            verify = True
        )
        return result.status_code is 200

    def generateRanges(self, start, end, period = None, format = None):
        period = period or self.period
        format = format or self.format
        end_tmp = start
        while end_tmp < end:
            start = end_tmp + timedelta(days = 1)
            end_tmp = start + timedelta(days = 7 * period)
            start_f = start.strftime(format)
            end_f = min(end, end_tmp).strftime(format)
            yield (start_f, end_f)

    def getEventsInRange(self, start, end):
        ranges = self.generateRanges(start, end)
        for range in ranges:
            url = 'https://flow.polar.com/training/getCalendarEvents?start=%s&end=%s' % range
            result = self.session.get(url)
            if result.status_code is 200:
                filename = '{}/{} - {}.json'.format(self.jsondir, range[0], range[1])
                self.logger.info('Writing event json to %s' % filename)
                file = open(filename, 'wb')
                file.write(result.text.encode('latin-1'))
                file.close()

    def downloadTraining(self, id):
        types = ('tcx', 'csv', 'gpx')
        for type in types:
            url = 'https://flow.polar.com/training/analysis/%d/export/%s/%s' % (id, type, str(self.zip).lower())
            result = self.session.get(url)
            if result.status_code is 200:
                content_disposition = result.headers['Content-Disposition']
                match = re.search('filename="([^"]+)";', content_disposition)
                if match is not None:
                    filename = '{}/{}'.format(self.datadir, match.group(1))
                    self.logger.info('Writing training to {}'.format(filename))
                    file = open(filename, 'wb')
                    file.write(result.text.encode('latin-1'))
                    file.close()

    def parseCalenderEvents(self):
        for root, dirs, filenames in os.walk(self.jsondir):
            for filename in filenames:
                self.logger.info('Parsing file %s' % filename)
                file = open('{}/{}'.format(root, filename), 'r')
                contents = json.load(StringIO(file.read()))
                file.close()
                for item in contents:
                    self.downloadTraining(item['listItemId'])

    def processTraining(self, session):
        proc = subprocess.Popen(['RScript','test.R', session], stdout = subprocess.PIPE, universal_newlines = True)
        while True:
          line = proc.stdout.readline()
          if line != '':
            print("test:", line.rstrip())
          else:
            break