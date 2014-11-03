# config: utf-8
from docopt import docopt
from resource.resource import Explorer, ResourceFilter
from logging import getLogger, StreamHandler, DEBUG
#from filefilter import filefilter
from syoboi_renamer.syoboi_renamer import SyoboiRenamer

usage = """Encoding Assistant

Usage:
    main.py trash
    main.py rename
"""

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
        for r in ex.resources:
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
        for r in ex.resources:
            LOG.debug(u'Try Rename {0}'.format(r.name))
            new_title = renamer.find(r)
            if new_title:
                ex.interactive_rename(r, new_title)


"""
def trash(file_filter):
    print('{0:*^80}'.format(' Trash '))
    file_filter.trash()


def move_pre_enc(file_filter):
    print('{0:*^80}'.format(' Move Pre-Encode '))
    file_filter.move_pre_enc()


def rename(file_filter):
    print('{0:*^80}'.format(' Rename Anime '))
    for unit in file_filter.tvtest_units:
        renamer = syoboi_renamer.SyoboiRenamer(unit)
        renamer.interpret()
"""


if __name__ == '__main__':
    args = docopt(usage, version='1.0.0')
    if args['trash']:
        Task.trash()
    if args['rename']:
        Task.rename()
    #file_filter = filefilter.FileFilter()
    # trash(file_filter)
    # rename(file_filter)
    # move_pre_enc(file_filter)
    #filefilter.move()
