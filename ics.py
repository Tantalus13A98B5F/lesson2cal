import vobject


class ICSCreator:
    def __init__(self):
        self._cal = vobject.iCalendar()

    def add_event(self, title, dtstart, dtend, location=None, rrule=None):
        vevent = self._cal.add('vevent')
        vevent.add('summary').value = title
        vevent.add('dtstart').value = dtstart
        vevent.add('dtend').value = dtend
        if location:
            vevent.add('location').value = location
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
