# coding: utf-8
import os
import requests
import configparser
import datetime
import re
from logging import getLogger, StreamHandler, DEBUG
from parse import parse


CONFIG_FILE = './config.ini'
LOG_LEVEL = DEBUG

LOG_HANDLER = StreamHandler()
LOG_HANDLER.setLevel(LOG_LEVEL)
LOG = getLogger(__name__)
LOG.setLevel(LOG_LEVEL)
LOG.addHandler(LOG_HANDLER)


class SyoboiRenamer:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding='utf-8')
        self.record_dir = self.config.get('directory', 'record')
        self.renamed_dir = self.config.get('directory', 'renamed')

    def find(self, resource):
        # check genre
        if resource.genre() != 'anime':
            return None
        # station
        station = self.detect_station(resource.name)
        # date
        date = datetime.datetime.fromtimestamp(os.stat(resource.ts_file).st_ctime)
        date += datetime.timedelta(minutes=1)
        date_str = self.detect_date(date)

        new_title = self.detect_new_title(date_str, station)
        return new_title

    def parse_input_filename(self, file_name):
        input_format = self.config.get('file', 'input_format')
        return parse(input_format, file_name)

    def detect_station(self, file_name):
        station = None
        try:
            station = self.parse_input_filename(file_name)['station']
            dup = re.match('(.+)\)-\(\d', station)
            if dup:
                station = dup.group(1)
            station = self.config['station'][station]
        except TypeError as e:
            LOG.error(u'Failed to parse input filename: {}'.format(file_name))
            raise Exception(u'Failed to parse input filename: {}'.format(e))
        except KeyError as e:
            LOG.error(u'No Such Station: {}'.format(station))
            raise Exception(u'No Such Station: {}'.format(e))
        return station

    @classmethod
    def detect_date(cls, date):
        if 0 <= date.hour <= 5:
            # convert 24H to 30H
            date -= datetime.timedelta(days=1)
            date_str = str(long(date.strftime('%Y%m%d%H%M')) + 2400)
        else:
            date_str = date.strftime('%Y%m%d%H%M')
        return date_str

    def detect_new_title(self, date_str, station):
        item = self.call_syoboi_api(date_str, station)
        title = self.escape(item['Title'])
        chapter = int(item['Count']) if item['Count'] is not None else 0
        subtitle = self.escape(item['SubTitle']) if item['SubTitle'] is not None else u''
        output_format = self.config.get('file', 'output_format')
        return output_format.format(title=title, chapter=chapter, subtitle=subtitle, station=station,
                                    date=date_str)

    @classmethod
    def call_syoboi_api(cls, date_str, station):
        rss2 = 'http://cal.syoboi.jp/rss2.php?alt=json&start={0}'.format(date_str)
        try:
            res = requests.get(rss2).json()
            for item in res['items']:
                if item['ChName'] == station:
                    return item
        except:
            raise Exception(u'Failed to get channel info')

    @classmethod
    def escape(cls, string):
        esc = {u'\\': u'＼', u'/': u'／', u':': u'：', u'*': u'＊', u'?': u'？',
               u'\"': u'”', u'<': u'＜', u'>': u'＞', u'|': u'｜'}
        for key, val in esc.items():
            string = string.replace(unicode(key), unicode(val))
        return string
