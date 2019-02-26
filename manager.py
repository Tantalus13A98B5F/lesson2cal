import datetime as dt
import logging
import re
from collections import namedtuple

from bs4 import BeautifulSoup
from utils import JAccountLoginManager, with_max_retries, proc_week_info, get_start_time, get_end_time, school_cal_generator
from ics import ICSCreator

__all__ = [
    'ElectSysManager'
]
logger = logging.getLogger('lesson2cal')


LessonInfo = namedtuple('LessonInfo',
                        'name campus room start end interval count lecturer comment')


class CalendarStylePolicy:
    def __init__(self, style):
        self._Location = self._LocationWithCampus if 'location' in style else self._LocationIndependent
        self._Remark = self._RemarkWithLecturer if 'teacher' in style else self._RemarkIndependent

        self.summary = self._NameWithLocation if 'name' in style else self._NameIndependent
        self.location = self._Empty if 'name' in style else self._Location
        self.description = self._Remark if 'remark' in style else self._Empty

    def __call__(self, cal, item):
        rrule = ICSCreator.rrule(item.interval, item.count) \
            if item.count > 1 else None
        cal.add_event(
            self.summary(item), item.start, item.end, self.location(item),
            description=self.description(item), rrule=rrule
        )

    def _LocationWithCampus(self, item):
        return "[%s]%s" % (item.campus, item.room)

    def _LocationIndependent(self, item):
        return item.room

    def _NameWithLocation(self, item):
        return "%s@%s" % (item.name, self._Location(item))

    def _NameIndependent(self, item):
        return item.name

    def _RemarkWithLecturer(self, item):
        return "%s | %s" % (item.lecturer, item.comment) if item.comment else item.lecturer

    def _RemarkIndependent(self, item):
        return item.comment

    def _Empty(self, item):
        return None


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

    @with_max_retries(3)
    def get_raw_data(self):
        tableurl = 'http://i.sjtu.edu.cn/xtgl/index_cxshjdAreaOne.html'
        dataurl = 'http://i.sjtu.edu.cn/kbcx/xskbcx_cxXsKb.html'
        rsp = self.session.get(tableurl)
        soup = BeautifulSoup(rsp.text, 'html.parser')
        args = {k: soup.find(id=k).attrs['value'] for k in ('xnm', 'xqm')}
        rsp2 = self.session.post(dataurl, args)
        self.raw_data = rsp2.json()
        return self.raw_data

    weekspan_pattern = re.compile(r'(\d+)-(\d+)周(\([单双]\))?')
    RawLesson = namedtuple('RawLesson',
                           'name campus room weeks weekday span lecturer comment')

    def _extract_lesson_list(self, rawdata, school_cal):
        rawlist = [
            self.RawLesson(
                obj['kcmc'], obj['xqmc'], obj['cdmc'], obj['zcd'],
                obj['xqj'], obj['jcs'], obj['xm'], obj['xkbz']
            ) for obj in rawdata['kbList']
        ]
        retlist = []
        for item in rawlist:
            match = self.weekspan_pattern.fullmatch(item.weeks)
            firstwk, lastwk, oddeven = match.groups()
            oddeven = int(oddeven == '单') if oddeven else None
            firstwk, interv, count = proc_week_info(firstwk, lastwk, oddeven)

            def calc_time(x):
                return school_cal(firstwk, int(item.weekday)-1, x)

            firstspan, lastspan = item.span.split('-')
            obj = LessonInfo(
                item.name, item.campus, item.room,
                calc_time(get_start_time(firstspan)),
                calc_time(get_end_time(lastspan)),
                interv, count, item.lecturer,
                item.comment if item.comment != '无' else '')
            retlist.append(obj)
        return retlist

    def convert_lessons_to_ics(self, firstday, calendar_style):
        school_cal = school_cal_generator(firstday)
        rawdata = self.get_raw_data()
        info = self._extract_lesson_list(rawdata, school_cal)
        cal = ICSCreator()
        calstylehandler = CalendarStylePolicy(calendar_style)
        for item in info:
            calstylehandler(cal, item)
        return cal
