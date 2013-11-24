# coding: utf-8
import sys
import requests


STATIONS = {'チバテレビ１': 'チバテレビ'}


# validation check
# now support only .ts.program.txt
def validate(argv):
    if len(argv) != 2:
        raise BaseException('too much arguments')
    if not '.ts.program.txt' in argv[1]:
        raise BaseException('not .ts.program.txt file')


# get tuple of datetime and station strings from .ts.program.txt file
def get_datetime_station(file_name):
    with open(file_name, encoding='cp932') as f:
        datetime = f.readline().rstrip()
        station = f.readline().rstrip()
    if datetime is None or station is None:
        raise BaseException('failed to read .ts.program.txt')
    if not station in STATIONS:
        raise BaseException('no such station : {0}'.format(station))
    return (datetime, STATIONS[station])


# input  : 2013/11/25(月) 01:30～02:00
# return : 201311242530
def convert_datetime(datetime):
    date = [int(i) for i in datetime[:10].split('/')]
    time = [int(i) for i in datetime[14:19].split(':')]
    # convert 24H to 30H
    if 0 <= time[0] <= 5:
        date[2] -= 1
        time[0] += 24
    return '{0[0]}{0[1]:02d}{0[2]:02d}{1[0]:02d}{1[1]:02d}'.format(date, time)


# call syoboi rss2 api
def get_channel_info(dt_start, station):
    rss2 = 'http://cal.syoboi.jp/rss2.php?alt=json&start={0}'.format(dt_start)
    try:
        res = requests.get(rss2).json()
        for item in res['items']:
            if item['ChName'] == station:
                return item
    except:
        raise BaseException('failed to get channel info from syoboi rss2 api')


# new title
def get_new_title(dic):
    return '{0}_#{1:02d}_「{2}」_({3})'.format(
           dic['Title'], int(dic['Count']), dic['SubTitle'], dic['ChName'])


if __name__ == '__main__':
    validate(sys.argv)
    (datetime, station) = get_datetime_station(sys.argv[1])
    dt_start = convert_datetime(datetime)
    channel_info = get_channel_info(dt_start, station)
    new_title = get_new_title(channel_info)

    print('--- ORIGIN ---')
    print(sys.argv[1])
    print('+++ RENAME +++')
    print(new_title)
