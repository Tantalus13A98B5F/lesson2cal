from collections import namedtuple
import datetime as dt
import vobject
import pytz
import csv
import sys


TIMEZONE = '''
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
BEGIN:STANDARD
DTSTART:16010101T000000
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
END:STANDARD
END:VTIMEZONE
'''
TZAsiaShanghai = pytz.timezone('Asia/Shanghai')


class ICSCreator:
    def __init__(self):
        self._cal = vobject.iCalendar()
        self._cal.add(vobject.readOne(TIMEZONE, validate=True))

    def add_event(self, title, dtstart, dtend, location='', description='', **rruleargs):
        vevent = self._cal.add('vevent')
        vevent.add('summary').value = title
        vevent.add('dtstart').value = TZAsiaShanghai.localize(dtstart)
        vevent.add('dtend').value = TZAsiaShanghai.localize(dtend)
        if location:
            vevent.add('location').value = location
        if description:
            vevent.add('description').value = description
        if rruleargs:
            vevent.add('rrule').value = self.rrule(**rruleargs)

    def serialize(self, filename=None):
        text = self._cal.serialize()
        if filename:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
        return text

    @classmethod
    def rrule(cls, interval=1, count=16, freq='WEEKLY'):
        data = {
            'FREQ': freq,
            'INTERVAL': interval,
            'COUNT': count
        }
        return ';'.join('%s=%s' % kv for kv in data.items())


class LessonTime:
    def __init__(self, num):
        if num == 13:
            self.start = dt.time(19, 40)
            self.end = dt.time(20, 20)
        elif num & 1:
            self.start = dt.time(7 + num, 0)
            self.end = dt.time(7 + num, 45)
        else:
            self.start = dt.time(6 + num, 55)
            self.end = dt.time(7 + num, 40)


class SchoolCalendar:
    def __init__(self, firstday):
        assert firstday.weekday() == 0
        self.first = firstday
    
    def getday(self, week, day):
        shift = dt.timedelta(days=(week-1)*7 + day-1)
        return lambda t: dt.datetime.combine(self.first, t) + shift


def main(infn, outfn, firstday):
    LessonInfo = namedtuple('LessonInfo',
        'invalid name loc firstwk lastwk weekday firstls lastls')
    ics = ICSCreator()
    cal = SchoolCalendar(firstday)
    with open(infn, encoding='gbk') as f:
        for item in csv.DictReader(f):
            item = LessonInfo(**item)
            item = LessonInfo(*item[:3], *[int(i) for i in item[3:]])
            if item.invalid: continue
            theday = cal.getday(item.firstwk, item.weekday)
            title = '{}@{}'.format(item.name, item.loc or 'unknown')
            dtstart = theday(LessonTime(item.firstls).start)
            dtend = theday(LessonTime(item.lastls).end)
            count = item.lastwk - item.firstwk + 1
            ics.add_event(title, dtstart, dtend, count=count)
    ics.serialize(outfn)


if __name__ == '__main__':
    main('lessons.csv', 'output.ics', dt.date(2020, 9, 7))
