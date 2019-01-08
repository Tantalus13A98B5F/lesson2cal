from bs4 import BeautifulSoup
from collections import namedtuple
import datetime as dt
import logging
import re
from utils import *


__all__ = [
    'ElectSysManager', 'NameAtLocPolicy', 'IndependentLocPolicy'
]
logger = logging.getLogger('lesson2cal')


LessonInfo = namedtuple('LessonInfo',
    'name localtion start end interval count comment')


class NameAtLocPolicy:
    def add_event(self, cal, item):
        rrule = ICSCreator.rrule(item.interval, item.count) \
            if item.count > 1 else None
        cal.add_event(
            item.name + '@' + item.location, item.start, item.end,
            description=item.comment, rrule=rrule
        )


class IndependentLocPolicy:
    def add_event(self, cal, item):
        rrule = ICSCreator.rrule(item.interval, item.count) \
            if item.count > 1 else None
        cal.add_event(
            item.name, item.start, item.end, item.location,
            description=item.comment, rrule=rrule
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

    @with_max_retries(3)
    def _get_raw_data(self):
        tableurl = 'http://i.sjtu.edu.cn/xtgl/index_cxshjdAreaOne.html'
        dataurl = 'http://i.sjtu.edu.cn/kbcx/xskbcx_cxXsKb.html'
        rsp = self.session.get(tableurl)
        soup = BeautifulSoup(rsp.text, 'html.parser')
        args = {k: soup.find(id=k).attrs['value'] for k in ('xnm', 'xqm')}
        rsp2 = self.session.post(dataurl, args)
        return rsp2.json()

    RawLesson = namedtuple('RawLesson',
        'name location weeks weekday span comment')
    weekspan_pattern = re.compile(r'(\d+)-(\d+)周(\([单双]\))?')

    def _extract_lesson_list(self, rawdata, school_cal):
        rawlist = [
            RawLesson(
                obj['kcmc'], obj['cdmc'], obj['zcd'],
                obj['xqj'], obj['jcs'], obj['xkbz'])
            for obj in rawdata['kbList']
        ]
        retlist = []
        for item in rawlist:
            match = weekspan_pattern.fullmatch(item.weeks)
            firstwk, lastwk, oddeven = match.groups()
            oddeven = int(oddeven == '单') if oddeven else None
            firstwk, interv, count = proc_week_info(firstwk, lastwk, oddeven)
            calc_time = lambda x: school_cal(firstwk, int(item.weekday)-1, x)
            firstspan, lastspan = item.span.split('-')
            obj = LessonInfo(
                item.name, item.localtion,
                calc_time(get_start_time(firstspan)),
                calc_time(get_end_time(lastspan)),
                interv, count,
                item.comment if item.comment != '无' else '')
            retlist.append(obj)
        return retlist

    def convert_lessons_to_ics(self, firstday, calstylepolicy):
        school_cal = school_cal_generator(firstday)
        rawdata = self._get_raw_data()
        info = self._extract_lesson_list(rawdata, school_cal)
        cal = ICSCreator()
        calstylehandler = calstylepolicy()
        for item in info:
            calstylehandler.add_event(cal, item)
        return cal
