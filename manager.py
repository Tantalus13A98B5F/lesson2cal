from bs4 import BeautifulSoup
import datetime as dt
import logging
import re
from utils import *


__all__ = [
    'ElectSysManager', 'NameAtLocPolicy', 'IndependentLocPolicy'
]
logger = logging.getLogger('lesson2cal')


class NameAtLocPolicy:
    def add_event(self, cal, item):
        rrule = ICSCreator.rrule(item['interval'], item['count']) if item['count'] > 1 else None
        cal.add_event(
            '%s@%s' % (item['name'], item['location']), item['start'], item['end'],
            description=item['comment'], rrule=rrule
        )


class IndependentLocPolicy:
    def add_event(self, cal, item):
        rrule = ICSCreator.rrule(item['interval'], item['count']) if item['count'] > 1 else None
        cal.add_event(
            item['name'], item['start'], item['end'], item['location'],
            description=item['comment'], rrule=rrule
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

    def convert_lessons_to_ics(self, firstday, calstylepolicy):
        # get raw data
        rsp = self.session.get('http://i.sjtu.edu.cn/xtgl/index_cxshjdAreaOne.html')
        soup = BeautifulSoup(rsp.text, 'html.parser')
        args = {k: soup.find(id=k).attrs['value'] for k in ('xnm', 'xqm')}
        rsp2 = self.session.post('http://i.sjtu.edu.cn/kbcx/xskbcx_cxXsKb.html', args)
        info = [
            {
                'name': obj['kcmc'],
                'span': obj['jcs'],
                'location': obj['cdmc'],
                'weeks': obj['zcd'],
                'weekday': obj['xqj'],
                'comment': obj['xkbz']
            }
            for obj in rsp2.json()['kbList']
        ]
        # proc data
        school_cal = school_cal_generator(firstday)
        weekspat = re.compile(r'(\d+)-(\d+)周(\([单双]\))?')
        for item in info:
            if item['comment'] == '无':
                item['comment'] = ''
            # proc weeks
            fw, lw, oddeven = weekspat.fullmatch(item['weeks']).groups()
            oddeven = int(oddeven == '单') if oddeven else None
            firstweek, lastweek = int(fw), int(lw)
            if oddeven is not None:
                if firstweek & 1 != oddeven:
                    firstweek += 1
                if lastweek & 1 != oddeven:
                    lastweek -= 1
            item['interval'] = 1 if oddeven is None else 2
            item['count'] = (lastweek - firstweek) // item['interval'] + 1
            # proc span
            weekday = int(item['weekday']) - 1
            a, b = item['span'].split('-')
            item['start'] = school_cal(firstweek, weekday, get_start_time(a))
            item['end'] = school_cal(firstweek, weekday, get_end_time(b))
        # generate cal file
        cal = ICSCreator()
        calstylehandler = calstylepolicy()
        for item in info:
            calstylehandler.add_event(cal, item)
        return cal

