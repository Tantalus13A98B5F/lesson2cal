from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from copy import copy
from time import sleep
from urllib import parse
import datetime as dt
import logging
import re
from utils import *


__all__ = [
    'ElectSysManager', 'NameAtLocPolicy', 'IndependentLocPolicy',
    'NoNotesPolicy', 'UnknownLocationNotePolicy', 'ULXCNotePolicy', 'FullNotesPolicy'
]
logger = logging.getLogger('lesson2cal')


class LessonInfo:
    lesson_pattern = re.compile(r'(.+)（(\d+)-(\d+)周）\[(.+)\](.周)?')

    def __init__(self, text, weekday, start_time, end_time):
        self.weekday = weekday
        self.start_time = start_time
        self.end_time = end_time
        self.description = ''
        groups = self.lesson_pattern.fullmatch(text).groups()
        name, firstwk, lastwk, loc, dsz = groups
        self.name = name
        self.first_week = int(firstwk)
        self.last_week = int(lastwk)
        self.location = loc
        self.interval = 2 if dsz else 1
        if dsz:
            remainder = 1 if dsz == '单周' else 0
            if self.first_week % 2 != remainder:
                self.first_week += 1
            if self.last_week % 2 != remainder:
                self.last_week -= 1

    @classmethod
    def trymerge(cls, lst):
        a, b = lst
        if a.name == b.name and a.location == b.location and \
                abs(a.first_week - b.first_week) == 1 and \
                abs(a.last_week - b.last_week) == 1 and \
                a.interval == b.interval == 2:
            a.first_week = min(a.first_week, b.first_week)
            a.last_week = max(a.last_week, b.last_week)
            a.interval = 1
            lst.pop()


class CalStylePolicyBase(metaclass=ABCMeta):
    def __init__(self, firstday):
        self.calc_dt = school_cal_generator(firstday)

    def _common_vars(self, item):
        _cnt = (item.last_week - item.first_week) // item.interval + 1
        rrule = ICSCreator.rrule(item.interval, _cnt) if _cnt > 1 else None
        dtstart = self.calc_dt(item.first_week, item.weekday, item.start_time)
        dtend = self.calc_dt(item.first_week, item.weekday, item.end_time)
        return rrule, dtstart, dtend

    @abstractmethod
    def add_event(self, cal, item):
        pass


class NameAtLocPolicy(CalStylePolicyBase):
    def add_event(self, cal, item):
        rrule, dtstart, dtend = self._common_vars(item)
        cal.add_event(
            '%s@%s' % (item.name, item.location), dtstart, dtend,
            description=item.description, rrule=rrule
        )


class IndependentLocPolicy(CalStylePolicyBase):
    def add_event(self, cal, item):
        rrule, dtstart, dtend = self._common_vars(item)
        cal.add_event(
            item.name, dtstart, dtend, item.location,
            description=item.description, rrule=rrule
        )


class NotesPolicyBase(metaclass=ABCMeta):
    def need_note(self, item) -> bool:
        return False

    def expand_note(self, item) -> 'list of items':
        return [item]


class NoNotesPolicy(NotesPolicyBase):
    pass


class UnknownLocationNotePolicy(NotesPolicyBase):
    def need_note(self, item):
        return '未定' in item.location


class ULXCNotePolicy(UnknownLocationNotePolicy):
    _regex = re.compile('\d+')

    def need_note(self, item):
        return super().need_note(item) or '形势与政策' in item.name

    def expand_note(self, item):
        if '形势与政策' in item.name:
            weeks = [int(i) for i in self._regex.findall(item.description)]
            ret = []
            for wk in weeks:
                new = copy(item)
                new.first_week = new.last_week = wk
                ret.append(new)
            return ret
        else:
            return super().expand_note(item)


class FullNotesPolicy(ULXCNotePolicy):
    def need_note(self, item):
        return True


class PageParser:
    starting_timelist = [
        dt.time(7+i, 55) if i % 2 else dt.time(8+i, 0)
        for i in range(14)
    ]
    ending_timelist = [dt.time(8+i, 40 if i % 2 else 45) for i in range(14)]
    base_url = 'http://electsys.sjtu.edu.cn/edu/newsBoard/newsInside.aspx'

    @classmethod
    def calc_timespan(cls, rownum, rowspan):
        starting = cls.starting_timelist[rownum]
        ending = cls.ending_timelist[rownum + rowspan - 1]
        return starting, ending

    def __init__(self, session, calstylehandler, noteshandler):
        self.session = session
        self.calstylehandler = calstylehandler
        self.noteshandler = noteshandler

    def main(self):
        logger.info('GET %s', self.base_url)
        rsp = self.session.get(self.base_url)
        logger.info('page return %s: %s', rsp.status_code, rsp.request.url)
        self.soup = BeautifulSoup(rsp.text, 'html.parser')
        self.extract_notes_url()
        raw = self.extract_raw_from_soup()
        converted = self.convert_and_merge_lessons(raw)
        final = self.handle_description(converted)
        return self.generate_ics(final)

    def handle_description(self, converted_iterable):
        for item in converted_iterable:
            if self.noteshandler.need_note(item):
                self.get_note(item)
                yield from self.noteshandler.expand_note(item)
            else:
                yield item

    def convert_and_merge_lessons(self, raw_iterable):
        for texts, ln, rn, rs in raw_iterable:
            op, ed = self.calc_timespan(rn, rs)
            lst = [LessonInfo(t, ln, op, ed) for t in texts]
            if len(lst) == 2:
                LessonInfo.trymerge(lst)
            yield from lst

    def extract_raw_from_soup(self):
        tbody = self.soup.find(class_='alltab')
        takenup = [[False for i in range(7)] for j in range(14)]
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
                    texts = [
                        i for i in tdobj.contents
                        if isinstance(i, str) and i.strip()
                    ]
                    yield texts, linenum, rownum, rowspan

    def extract_notes_url(self):
        note_table = self.soup.find('table', id='Datagrid1')
        self.notes_url = {}
        for trobj in note_table.find_all('tr')[1:]:
            tdlist = trobj.find_all('td')
            name = tdlist[1].text.strip()
            href = tdlist[3].a['href']
            self.notes_url[name] = parse.urljoin(self.base_url, href)

    @with_max_retries(2)
    def get_note(self, item):
        url = self.notes_url[item.name]
        sleep(5)
        logger.info('GET %s', url)
        rsp = self.session.get(url)
        logger.info('page return %s: %s', rsp.status_code, rsp.request.url)
        if rsp.request.url != url:
            qs = take_qs(rsp.request.url)
            msg = qs.get('message', [''])[0]
            logger.info('ElectSys say: %s', msg)
            logger.info('will retry after 1 min')
            sleep(60)
            raise Exception('retry plz')
        soup = BeautifulSoup(rsp.text, 'html.parser')
        note_regex = re.compile('备注.*')
        td = soup.find('td', text=note_regex)
        text = td.text[3:].strip()
        item.description = text

    def generate_ics(self, lesson_list):
        cal = ICSCreator()
        for item in lesson_list:
            self.calstylehandler.add_event(cal, item)
        return cal


class ElectSysManager(JAccountLoginManager):
    def get_login_url(self):
        return 'http://electsys.sjtu.edu.cn/edu/login.aspx'

    def check_login_result(self, rsp):
        ret = super().check_login_result(rsp)
        if ret:
            return ret
        success_url = 'http://electsys.sjtu.edu.cn/edu/student/sdtMain.aspx'
        if rsp.request.url == success_url:
            return ''
        if 'electsys.sjtu.edu.cn' in rsp.request.url:
            qs = take_qs(rsp.request.url)
            msg = qs.get('message', [''])[0]
            if msg:
                return 'ElectSys says: ' + msg
        return '未知错误'

    def convert_lessons_to_ics(self, firstday, calstylepolicy, notespolicy):
        parser = PageParser(self.session, calstylepolicy(firstday), notespolicy())
        return parser.main()
