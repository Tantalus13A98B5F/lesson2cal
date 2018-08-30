from collections import namedtuple
from bs4 import BeautifulSoup
import datetime as dt
import re
from utils import JAccountLoginManager
from ics import ICSCreator


LessonInfo = namedtuple(
    'LessonInfo', 
    [
        'name', 'first_week', 'last_week', 'location',
        'interval', 'start_time', 'end_time', 'weekday'
    ]
)
starting_timelist = [
    dt.time(7+i, 55) if i % 2 else dt.time(8+i, 0)
    for i in range(14)
]
ending_timelist = [dt.time(8+i, 40 if i%2 else 45) for i in range(14)]
lesson_pattern = re.compile(r'(.+)（(\d+)-(\d+)周）\[(.+)\](.周)?')


def generate_ics(lesson_list, firstday):
    cal = ICSCreator()
    for item in lesson_list:
        shift_days = dt.timedelta(days=(item.first_week - 1)*7 + item.weekday)
        count = (item.last_week - item.first_week) // item.interval + 1
        dtstart = dt.datetime.combine(firstday, item.start_time) + shift_days
        dtend = dt.datetime.combine(firstday, item.end_time) + shift_days
        cal.add_event(
            '%s@%s' % (item.name, item.location),
            dtstart, dtend, cal.rrule(item.interval, count)
        )
    return cal


class LessonTemp:
    def __init__(self, name, first_week, last_week, location, oddeven):
        self.name = name
        self.first_week = int(first_week)
        self.last_week = int(last_week)
        self.location = location
        self.interval = 2 if oddeven else 1
        if oddeven:
            remainder = 1 if oddeven == '单周' else 0
            if self.first_week % 2 != remainder:
                self.first_week += 1
            if self.last_week % 2 != remainder:
                self.last_week -= 1

    def trymerge(self, b):
        if self.name == b.name and self.location == b.location and \
                abs(self.first_week - b.first_week) <= 1 and \
                abs(self.last_week - b.last_week) <= 1 and \
                self.interval == b.interval == 2:
            self.first_week = min(self.first_week, b.first_week)
            self.last_week = max(self.last_week, b.last_week)
            self.interval = 1
            return True
        return False


def proc_lesson(tdobj, linenum, rownum, rowspan):
    # convert
    weekday = linenum
    starting = starting_timelist[rownum]
    ending = ending_timelist[rownum + rowspan - 1]
    texts = (
        i for i in tdobj.contents
        if isinstance(i, str) and i.strip()
    )
    lesson_templist = [
        LessonTemp(*lesson_pattern.fullmatch(i).groups())
        for i in texts
    ]
    # merge
    if len(lesson_templist) == 2:
        a, b = lesson_templist
        if a.trymerge(b):
            lesson_templist.pop()
    # final
    lesson_info = [
        LessonInfo(
            item.name, item.first_week, item.last_week, item.location,
            item.interval, starting, ending, weekday
        ) for item in lesson_templist
    ]
    return lesson_info


def extract_lessons_from_soup(soup):
    tbody = soup.find(attrs={'class': 'alltab'})
    takenup = [[False for i in range(7)] for j in range(14)]
    lesson_list = []
    for rownum, trobj in enumerate(tbody.find_all('tr')[1:]):
        tdit = iter(trobj.find_all('td'))
        next(tdit)
        for linenum in range(7):
            if takenup[rownum][linenum]:
                continue
            tdobj = next(tdit)
            if tdobj.text.strip():
                rowspan = int(tdobj.attrs.get('rowspan', 1))
                for i in range(rowspan):
                    takenup[rownum + i][linenum] = True
                lesson_list.extend(proc_lesson(tdobj, linenum, rownum, rowspan))
    return lesson_list


class ElectSysManager(JAccountLoginManager):
    def get_login_url(self):
        return 'http://electsys.sjtu.edu.cn/edu/login.aspx'

    def check_login_result(self, rsp):
        ret = super().check_login_result(rsp)
        if ret:
            return ret
        success_url = 'http://electsys.sjtu.edu.cn/edu/student/sdtMain.aspx'
        return '' if rsp.request.url == success_url else rsp.request.url
    
    def convert_lessons_to_ics(self, firstday):
        url = 'http://electsys.sjtu.edu.cn/edu/newsBoard/newsInside.aspx'
        rsp = self.session.get(url)
        soup = BeautifulSoup(rsp.text, 'html.parser')
        lesson_list = extract_lessons_from_soup(soup)
        return generate_ics(lesson_list, firstday)
