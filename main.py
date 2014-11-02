# config: utf-8
from filefilter import filefilter
from syoboi_renamer import syoboi_renamer

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

if __name__ == '__main__':
    file_filter = filefilter.FileFilter()
    #trash(file_filter)
    #rename(file_filter)
    move_pre_enc(file_filter)
    #filefilter.move()
