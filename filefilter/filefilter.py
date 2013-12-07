# coding: utf-8

import os
import glob
import configparser
import re
import json
import datetime


class FileFilter:
    def __init__(self):
        # read configs
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        # directory
        self.record_dir = self.config.get('directory', 'record')
        self.trash_dir = self.config.get('directory', 'trash')
        self.broken_dir = self.config.get('directory', 'broken')
        # lists
        #   .ts file list
        self.units = self.__get_units()
        #   not have any of '.ts', '.ts.err' and '.ts.program.txt'
        self.lack_units = []
        #   '.ts' may be broken
        self.broken_units = []
        # to trash
        self.trash_units = []
        #   have all of '.ts', '.ts.err' and '.ts.program.txt'
        self.tvtest_units = []
        # filter units
        self.__filter()
        self.trash()

    # search units from the 'record' directoy
    def __get_units(self):
        ts_list = glob.glob('{0}*.ts'.format(self.record_dir))
        return list(map(lambda x: x[len(self.record_dir):-len('.ts')],
                        ts_list))

    def __to_trash(self, file_name):
        blacklist = json.loads(self.config.get('pattern', 'blacklist'))
        whitelist = json.loads(self.config.get('pattern', 'whitelist'))
        if re.search('\)-\(\d\)', file_name):
            return True
        for w_word in whitelist:
            if w_word in file_name:
                return False
        for b_word in blacklist:
            if b_word in file_name:
                return True

    def __is_passed_enough_time(self, file_name):
        full_path = '{0}{1}'.format(self.record_dir, file_name)
        last_update = datetime.datetime.fromtimestamp(
            os.stat(full_path).st_mtime)
        now = datetime.datetime.now()
        if (last_update + datetime.timedelta(hours=12) < now):
            return True

    # expect to have '.ts', '.ts.err' and '.ts.program.txt'
    def __is_lack_unit(self, unit):
        unit_len = len(glob.glob('{0}{1}*'.format(self.record_dir, unit)))
        return False if unit_len == 3 else True

    def __filter(self):
        for unit in self.units:
            # time filter
            if not self.__is_passed_enough_time('{0}.ts'.format(unit)):
                continue
            # word filter
            if self.__to_trash(unit):
                self.trash_units.append(unit)
                continue
            # broken filter
            #   TODO: later
            if not self.__is_lack_unit(unit):
                self.tvtest_units.append(unit)

    def trash(self):
        for unit in self.trash_units:
            print(glob.glob('{0}{1}*'.format(self.record_dir, unit)))
            #shutil.move(self.record_dir + file_name, trash_dir)
