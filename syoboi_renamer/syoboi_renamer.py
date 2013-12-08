# coding: utf-8
import sys
import requests
import configparser
import datetime
import re
import shutil

class SyoboiRenamer:
    def __init__(self, unit):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        self.unit = unit
        self.record_dir = self.config.get("directory", "record")
        self.renamed_dir = self.config.get("directory", "renamed")
        self.ts_path = "{0}{1}.ts".format(self.record_dir, unit)
        self.err_path = "{0}{1}.ts.err".format(self.record_dir, unit)
        self.program_path = "{0}{1}.ts.program.txt".format(self.record_dir, unit)
        self.is_anime, self.date_time, self.station = self.__get_datetime_station()
        self.date_time = self.__convert_datetime(self.date_time)
        self.channel_info = self.__get_channel_info(self.date_time, self.station)
        self.new_title = self.__get_new_title()

    # get tuple of datetime and station strings from .ts.program.txt file
    def __get_datetime_station(self):
        with open(self.program_path, encoding='cp932') as f:
            date_time = f.readline().rstrip()
            station = f.readline().rstrip()
            if re.search("アニメ／特撮 - 国内アニメ", f.read()):
                is_anime = True
            else:
                is_anime = False
        if date_time is None or station is None:
            raise BaseException('failed to read .ts.program.txt')
        if not station in self.config['station']:
            raise BaseException('no such station : {0}'.format(station))
        return (is_anime, date_time, self.config['station'][station])

    # input  : 2013/11/25(月) 01:30～02:00
    # return : 201311242530
    def __convert_datetime(self, date_time):
        date = [int(i) for i in date_time[:10].split('/')]
        time = [int(i) for i in date_time[14:19].split(':')]
        # convert 24H to 30H
        if 0 <= time[0] <= 5:
            date = datetime.date(date[0], date[1], date[2]) 
            date = date - datetime.timedelta(days=1)
            date = date.strftime('%Y%m%d')
            time[0] += 24
        else:
            date = "{0}{1:02d}{2:02d}".format(date[0], date[1], date[2])
        return '{0}{1[0]:02d}{1[1]:02d}'.format(date, time)

    # call syoboi rss2 api
    def __get_channel_info(self, dt_start, station):
        rss2 = 'http://cal.syoboi.jp/rss2.php?alt=json&start={0}'.format(dt_start)
        try:
            res = requests.get(rss2).json()
            for item in res['items']:
                if item['ChName'] == station:
                    return item
        except:
            raise BaseException('failed to get channel info from syoboi rss2 api')

    # new title
    def __get_new_title(self):
        dic = self.channel_info
        return '{0}_#{1:02d}_「{2}」_({3})_{4}'.format(
               dic['Title'], int(dic['Count']), dic['SubTitle'], dic['ChName'], self.date_time)

    def __rename(self):
        print()
        # backup origin name to .ts.program.txt
        with open(self.program_path, 'a') as f:
            f.write('\nOrignName : {0}\n'.format(self.unit))
        # rename and move to renamed directory
        for ext in ['.ts', '.ts.err', '.ts.program.txt']:
            shutil.move(self.record_dir + self.unit + ext,
                    self.renamed_dir + self.new_title + ext)

    def interpret(self):
        print('[BEFORE] {0}'.format(self.unit))
        if not self.is_anime:
            print('This file is not anime ...Skip...')
            return 1
        print('[AFTER ] {0}'.format(self.new_title))
        ans = input('Rename it? [y/N] ')
        if ans == 'y':
            self.__rename()
            print('!!! Renamed !!!')
        else:
            print('... Skip ...') 
        return 0
