# config: utf-8
from filefilter import filefilter
from syoboi_renamer import syoboi_renamer

if __name__ == '__main__':
    file_filter = filefilter.FileFilter()
    print('{0:*^80}'.format(' Trash '))
    file_filter.trash()
    print('{0:*^80}'.format(' Rename Anime '))
    for unit in file_filter.tvtest_units:
        renamer = syoboi_renamer.SyoboiRenamer(unit)
        renamer.interpret()