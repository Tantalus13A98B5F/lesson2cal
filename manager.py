import datetime as dt
import logging
import re
from collections import namedtuple

from bs4 import BeautifulSoup
from ics import ICSCreator
from utils import *

__all__ = [
    'ElectSysManager'
]
logger = logging.getLogger('lesson2cal')


LessonInfo = namedtuple('LessonInfo',
                        'name campus room start end interval count lecturer comment')


class CalendarStylePolicy:
    def __init__(self, style):
        return_empty = lambda x: None
        if 'campus' in style:
            get_location = lambda it: "[%s]%s" % (it.campus, it.room)
        else:
            get_location = lambda it: it.room
        if 'name@loc' in style:
            self.summary = lambda it: it.name + '@' + get_location(it)
            self.location = return_empty
        else:
            self.summary = lambda it: it.name
            self.location = get_location
        if 'remark' in style:
            if 'teacher' in style:
                self.description = lambda it: \
                    it.lecturer + (it.comment and ' | ' + it.comment)
            else:
                self.description = lambda it: it.comment
        else:
            self.description = return_empty

    def __call__(self, cal, item):
        rrule = ICSCreator.rrule(item.interval, item.count) \
            if item.count > 1 else None
        cal.add_event(
            self.summary(item), item.start, item.end, self.location(item),
            description=self.description(item), rrule=rrule
        )


class ElectSysManager(JAccountLoginManager):
    def get_login_url(self):
        return 'http://i.sjtu.edu.cn/jaccountlogin'

    def check_login_result(self, rsp):
        ret = super().check_login_result(rsp)
        if ret:
            return ret
        success_url = 'http://i.sjtu.edu.cn/xtgl/index_initMenu.html'
        if rsp.request.url.startswith(success_url):
            return ''
        return '未知错误'

    def semester_args(self, xnm, xqm):
        return {
            'xnm': str(xnm),
            'xqm': str({1:3, 2:12, 3:16}[int(xqm)])
        }
    
    @with_max_retries(3)
    def get_semesters(self):
        tableurl = 'http://i.sjtu.edu.cn/xtgl/index_cxshjdAreaOne.html'
        rsp = self.session.get(tableurl)
        soup = BeautifulSoup(rsp.text, 'html.parser')
        sfind = lambda k: soup.find(id=k).attrs['value']
        return [
            {'xnm': sfind('xnm'), 'xqm': sfind('xqm')},
            {'xnm': sfind('xxnm'), 'xqm': sfind('xxqm')}
        ]

    @with_max_retries(3)
    def get_raw_data(self, semester):
        dataurl = 'http://i.sjtu.edu.cn/kbcx/xskbcx_cxXsKb.html'
        rsp2 = self.session.post(dataurl, semester)
        self.raw_data = rsp2.json()
        return self.raw_data

    def _extract_lesson_list(self, rawdata, school_cal):
        weekspan_pattern = re.compile(r'(\d+)-(\d+)周(\([单双]\))?')
        RawLesson = namedtuple(
            'RawLesson',
            'name campus room weeks weekday span lecturer comment'
        )
        rawlist = [
            RawLesson(
                obj['kcmc'], obj['xqmc'], obj['cdmc'], obj['zcd'],
                obj['xqj'], obj['jcs'], obj['xm'], obj['xkbz']
            ) for obj in rawdata['kbList']
        ]
        retlist = []
        for item in rawlist:
            match = weekspan_pattern.fullmatch(item.weeks)
            firstwk, lastwk, oddeven = match.groups()
            oddeven = int(oddeven == '(单)') if oddeven else None
            firstwk, interv, count = proc_week_info(firstwk, lastwk, oddeven)
            school_cal_time = lambda x: school_cal(firstwk, int(item.weekday)-1, x)
            firstspan, lastspan = item.span.split('-')
            obj = LessonInfo(
                item.name, item.campus, item.room,
                school_cal_time(get_start_time(firstspan)),
                school_cal_time(get_end_time(lastspan)),
                interv, count, item.lecturer,
                item.comment if item.comment != '无' else '')
            retlist.append(obj)
        return retlist

    def convert_lessons_to_ics(self, firstday, calendar_style):
        school_cal = school_cal_generator(firstday)
        info = self._extract_lesson_list(self.rawdata, school_cal)
        cal = ICSCreator()
        add_event = CalendarStylePolicy(calendar_style)
        for item in info:
            add_event(cal, item)
        return cal
