import vobject
import pytz


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

    def add_event(self, title, dtstart, dtend, location='', description='', \
            rrule=None):
        vevent = self._cal.add('vevent')
        vevent.add('summary').value = title
        vevent.add('dtstart').value = TZAsiaShanghai.localize(dtstart)
        vevent.add('dtend').value = TZAsiaShanghai.localize(dtend)
        if location:
            vevent.add('location').value = location
        if description:
            vevent.add('description').value = description
        if rrule:
            vevent.add('rrule').value = rrule

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
