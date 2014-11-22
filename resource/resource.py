# coding: utf-8
import configparser
import datetime
import glob
import os
import codecs
import re
import json
import shutil
from logging import getLogger, StreamHandler, DEBUG

CONFIG_FILE = './config.ini'
ENOUGH_TIME_HOUR = 12
LOG_LEVEL = DEBUG

LOG_HANDLER = StreamHandler()
LOG_HANDLER.setLevel(LOG_LEVEL)
LOG = getLogger(__name__)
LOG.setLevel(LOG_LEVEL)
LOG.addHandler(LOG_HANDLER)


class Resource:
    def __init__(self, ts_file):
        self.name = os.path.basename(ts_file).split('.ts')[0]
        self.dir = os.path.dirname(ts_file)
        self.ts_file = ts_file
        self.program_file = self.get_program_file()
        self.error_file = self.get_error_file()

    def get_program_file(self):
        f = os.path.join(self.dir, self.name + '.ts.program.txt')
        return f if os.path.exists(f) else None

    def get_error_file(self):
        f = os.path.join(self.dir, self.name + '.ts.err')
        return f if os.path.exists(f) else None

    def size(self):
        return os.path.getsize(self.ts_file)

    def genre(self):
        if self.program_file:
            with codecs.open(self.program_file, encoding='cp932') as f:
                buf = f.read()
                if re.search(u'国内アニメ', buf):
                    return 'anime'
                elif re.search(u'バラエティ', buf):
                    return 'variety'
                elif re.search(u'ドラマ', buf):
                    return 'drama'
        return 'unknown'

    def is_passed_enough_time(self):
        last_update = datetime.datetime.fromtimestamp(os.stat(self.ts_file).st_mtime)
        current_timestamp = datetime.datetime.now()
        is_enough_time = last_update + datetime.timedelta(hours=ENOUGH_TIME_HOUR) < current_timestamp
        return True if is_enough_time else False

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name.encode('cp932')


class Explorer:
    def __init__(self):
        # read configs
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding='utf-8')
        # directories
        self.record_dir = self.config.get('directory', 'record')
        self.trash_dir = self.config.get('directory', 'trash')
        self.broken_dir = self.config.get('directory', 'broken')
        self.renamed_dir = self.config.get('directory', 'renamed')
        self.encode_dir = self.config.get('directory', 'encode')

    def get_recorded_ts(self, directory=None):
        if directory is None:
            directory = self.record_dir
        else:
            if not os.path.exists(directory):
                LOG.error(u'No Such Directory: {}'.format(directory))
                raise Exception('No Such Directory')
        return [s.decode('cp932') for s in glob.glob('{0}*.ts'.format(directory))]

    def resources(self, directory=None):
        resources = [Resource(ts) for ts in self.get_recorded_ts(directory)]
        return filter(lambda x: x.is_passed_enough_time(), resources)

    def duplicates(self):
        dupes = []
        for resource in self.resources():
            dup = re.search(u'\)-\(\d\)', resource.name)
            if dup:
                base_name = os.path.join(resource.dir, resource.name[:dup.start() + 1])
                if len(filter(lambda x: base_name in x.ts_file, self.resources())) >= 2:
                    dupes.append(base_name)
        return dupes

    def rename(self, resource, new_name):
        if resource.program_file:
            # backup origin name to .ts.program.txt
            with codecs.open(resource.program_file, mode='a', encoding='cp932') as f:
                f.write(u'\nOriginName : {0}'.format(resource.name))
        self.move(resource, self.renamed_dir, new_name)

    def interactive_rename(self, resource, new_name):
        print u'[BEFORE] {0}'.format(resource.name)
        print u'[AFTER ] {0}'.format(new_name)
        ans = raw_input(u'Rename it? [y/N/e]')
        if ans == u'y':
            self.rename(resource, new_name)
            print u'![Renamed]!'
        elif ans == u'e':
            exit(u'Bye')
        else:
            print u'[Skip]'

    @classmethod
    def move(cls, resource, dst_dir, dst_name=None):
        if dst_name is None:
            dst_name = resource.name
        LOG.debug(u'![Move]! {0} : {1} -> {2}'.format(dst_name, resource.dir, dst_dir))
        for ext in [u'.ts', u'.ts.program.txt', u'.ts.err']:
            dst_file = os.path.join(dst_dir, dst_name + ext)
            if os.path.exists(dst_file):
                raise Exception(u'File already exist: {0}'.format(dst_file))
            src_file = os.path.join(resource.dir, resource.name + ext)
            if os.path.exists(src_file):
                shutil.move(src_file, dst_file)

    def trash(self, resource):
        if not resource.is_passed_enough_time():
            return False
        LOG.info(u'![trash]! {0}'.format(resource.name))
        files = filter(lambda x: x is not None, [resource.ts_file, resource.program_file, resource.error_file])
        for f in files:
            shutil.move(f, self.trash_dir)
        return True

    def move_pre_enc(self, length):
        window_size_dict = {}
        for k, v in dict(self.config.items(u'window_size')).items():
            window_size_dict[k] = json.loads(v)
        resources = self.resources(self.renamed_dir)
        for resource in resources:
            if length < 1:
                break
            try:
                station = resource.name.split('_')[-2][1:-1]
            except:
                raise BaseException(u'Fail to detect station name: {0}'.format(resource))
            window_size = u''
            for size, stations in window_size_dict.items():
                if station in stations:
                    window_size = size
            if window_size == u'':
                raise BaseException('No such station in window_size: {0}'.format(station))
            dst_dir = os.path.join(self.encode_dir, u'anime_{0}'.format(window_size))
            self.move(resource, dst_dir)
            length -= 1


class ResourceFilter:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    blacklist = json.loads(config.get('pattern', 'blacklist'))

    def __init__(self):
        pass

    @classmethod
    def is_in_blacklist(cls, resource):
        for word in cls.blacklist:
            if word in resource.name:
                return True

    @classmethod
    def duplicates(cls, base_name):
        # /path/to/file (exclude `-(n)` and `.ts`)
        LOG.debug(u'  - {0}'.format(base_name))
        dupes = []
        # /path/to/file.ts (non `-(n)` file)
        if os.path.exists(base_name + u'.ts'):
            r = Resource(base_name + u'.ts')
            LOG.debug(u'    - [{0: >12}] {1}'.format(r.size(), r.name))
            dupes.append(r)
        # /path/to/file-(n).ts (include `-(n)` files)
        i = 1
        while True:
            f = u'{0}-({1}).ts'.format(base_name, i)
            if os.path.exists(f):
                r = Resource(f)
                LOG.debug(u'    - [{0: >12}] {1}'.format(r.size(), r.name))
                dupes.append(r)
                i += 1
            else:
                break
        max_ts_file = max(dupes, key=lambda x: x.size())
        dupes.remove(max_ts_file)
        return dupes
