# config: utf-8
from docopt import docopt
from resource.resource import Explorer, ResourceFilter
from logging import getLogger, StreamHandler, DEBUG
# from filefilter import filefilter
from syoboi_renamer.syoboi_renamer import SyoboiRenamer
from tmpgencvmw5.assistant import Assistant
import configparser

usage = """Encoding Assistant

Usage:
    main.py trash
    main.py rename
    main.py setup (-t | -s | --path <path>)
    main.py move_pre_enc (-l <length>)
"""

CONFIG_FILE = './config.ini'

LOG_LEVEL = DEBUG
LOG_HANDLER = StreamHandler()
LOG_HANDLER.setLevel(LOG_LEVEL)
LOG = getLogger(__name__)
LOG.setLevel(LOG_LEVEL)
LOG.addHandler(LOG_HANDLER)


class Task:
    def __init__(self):
        pass

    @classmethod
    def trash(cls):
        LOG.debug('{0:*^80}'.format(' Trash '))
        ex = Explorer()
        LOG.debug('{0:-^80}'.format('Trash Blacklist'))
        for r in ex.resources():
            if ResourceFilter.is_in_blacklist(r):
                ex.trash(r)
        LOG.debug('{0:-^80}'.format('Trash Duplicate'))
        for d in ex.duplicates():
            map(lambda x: ex.trash(x), ResourceFilter.duplicates(d))

    @classmethod
    def rename(cls):
        LOG.debug('{0:*^80}'.format(' Rename '))
        renamer = SyoboiRenamer()
        ex = Explorer()
        for r in ex.resources():
            LOG.debug(u'Try Rename {0}'.format(r.name))
            new_title = renamer.find(r)
            if new_title:
                ex.interactive_rename(r, new_title)

    @classmethod
    def setup(cls, work_dir):
        LOG.debug('{0:*^80}'.format(' Setup TMPGEncVMW5 '))
        assistant = Assistant()
        ex = Explorer()
        assistant.add_files(ex.resources(work_dir))

    @classmethod
    def move_pre_enc(cls, length):
        LOG.debug('{0:*^80}'.format(' Move Pre-Encode '))
        Explorer().move_pre_enc(length)


if __name__ == '__main__':
    args = docopt(usage, version='1.0.0')
    if args['trash']:
        Task.trash()
    if args['rename']:
        Task.rename()
    if args['setup']:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE, encoding='utf-8')
        work_dir = None
        if args['-t']:
            work_dir = config.get('directory', 'workspace_t')
        if args['-s']:
            work_dir = config.get('directory', 'workspace_s')
        if args['--path']:
            work_dir = args['<path>']
        Task.setup(work_dir)
    if args['move_pre_enc']:
        Task.move_pre_enc(int(args['<length>']))
        # file_filter = filefilter.FileFilter()
        # trash(file_filter)
        # rename(file_filter)
        # move_pre_enc(file_filter)
        # filefilter.move()
