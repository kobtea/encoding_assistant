# coding: utf-8
import os
import glob
import configparser
import re
import json
import datetime
import shutil


class FileFilter:
    def __init__(self):
        # read configs
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        # directory
        self.record_dir = self.config.get('directory', 'record')
        self.trash_dir = self.config.get('directory', 'trash')
        self.broken_dir = self.config.get('directory', 'broken')
        self.renamed_dir = self.config.get('directory', 'renamed')
        self.encode_dir = self.config.get('directory', 'encode')
        # lists
        # .ts file list
        self.units = self.__get_units(self.record_dir)
        # not have any of '.ts', '.ts.err' and '.ts.program.txt'
        self.lack_units = []
        #   '.ts' may be broken
        self.broken_units = []
        # to trash
        self.trash_units = []
        #   have all of '.ts', '.ts.err' and '.ts.program.txt'
        self.tvtest_units = []
        # filter units
        self.__filter()

    # search units from the 'record' directoy
    def __get_units(self, dir):
        ts_list = glob.glob('{0}*.ts'.format(dir))
        return list(map(lambda x: x[len(dir):-len('.ts')], ts_list))

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
        if 'フジテレビ' in file_name and not '[字]' in file_name:
            return True
        return False

    def __is_passed_enough_time(self, file_name):
        full_path = '{0}{1}'.format(self.record_dir, file_name)
        last_update = datetime.datetime.fromtimestamp(
            os.stat(full_path).st_mtime)
        now = datetime.datetime.now()
        if (last_update + datetime.timedelta(hours=12) < now):
            return True

    # expect to have '.ts', '.ts.err' and '.ts.program.txt'
    def __is_lack_unit(self, unit):
        if not os.path.exists("{0}{1}.ts".format(self.record_dir, unit)):
            return True
        if not os.path.exists("{0}{1}.ts.err".format(self.record_dir, unit)):
            return True
        if not os.path.exists("{0}{1}.ts.program.txt".format(self.record_dir, unit)):
            return True
        return False

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
            # TODO: later
            if not self.__is_lack_unit(unit):
                self.tvtest_units.append(unit)

    def trash(self):
        for unit in self.trash_units:
            print(unit)
            for ext in ['.ts', '.ts.err', '.ts.program.txt']:
                shutil.move(self.record_dir + unit + ext, self.trash_dir)

    def move_pre_enc(self):
        window_size_dict = self.config._sections['window_size']
        units = self.__get_units(self.renamed_dir)
        break_count = 80
        for unit in units:
            if break_count <= 0:
                break
            print(unit)
            elms = unit.split('_')
            title = elms[0]
            station = elms[-2][1:-1]
            window_size = ""
            for size, stations in window_size_dict.items():
                if station in window_size_dict[size]:
                    window_size = size
                    break
            if window_size == "":
                raise BaseException("No Such Station in window_size : {0}".format(station))
            # move to encode dir
            dst_dir = '{0}anime_{1}\\'.format(self.encode_dir, window_size)
            for ext in ['.ts', '.ts.err', '.ts.program.txt']:
                shutil.move(self.renamed_dir + unit + ext, dst_dir)
            break_count -= 1


def move():
    # read configs
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    move_src_dir = config.get('directory', 'move')
    move_dst_dir = json.loads(config.get('directory', 'move_dst'))
    move_ts_dst_dir = config.get('directory', 'move_ts_dst')
    moved_trash_dir = config.get('directory', 'moved_trash')
    for file_name in os.listdir(move_src_dir):
        splits = file_name.split('_')
        title = splits[0]
        ext = re.match('\d+(.+)', splits[-1]).group(1)
        dst_dirs = []
        if ext == '.ts':
            print('[ts] : {0}'.format(file_name))
            dst_dir = '{0}{1}'.format(move_ts_dst_dir, title)
            if not os.path.exists(dst_dir):
                print('Create Dir : {0}'.format(dst_dir))
                os.mkdir(dst_dir)
            dst_dir = '{0}{1}\\ts'.format(move_ts_dst_dir, title)
            if not os.path.exists(dst_dir):
                print('Create Dir : {0}'.format(dst_dir))
                os.mkdir(dst_dir)
            dst_dirs.append(dst_dir)
        elif ext == '.mp4':
            print('[mp4] : {0}'.format(file_name))
            for dst_dir in move_dst_dir:
                dst_dir = dst_dir + title
                if not os.path.exists(dst_dir):
                    print('Create Dir : {0}'.format(dst_dir))
                    os.mkdir(dst_dir)
                dst_dirs.append(dst_dir)
        elif ext in ['.ts.err', '.ts.program.txt']:
            print('[meta] : {0}'.format(file_name))
            for dst_dir in move_dst_dir:
                dst_dir = '{0}{1}\\metadata'.format(dst_dir, title)
                if not os.path.exists(dst_dir):
                    print('Create Dir : {0}'.format(dst_dir))
                    os.mkdir(dst_dir)
                dst_dirs.append(dst_dir)
        else:
            raise BaseException('anything bad at filefilter.move : {0}'.format(file_name))
        # Copy
        for dst_dir in dst_dirs:
            if os.path.exists('{0}\\{1}'.format(dst_dir, file_name)):
                print('This file already exists ... skip')
                continue
            print('Copy to : {0} ...'.format(dst_dir), end='')
            shutil.copy(move_src_dir + file_name, dst_dir)
            print('done')
        shutil.move(move_src_dir + file_name, moved_trash_dir)
