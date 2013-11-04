import icalendar
import requests

from ode.models import DBSession, Source, Event
from deserializers import icalendar_to_event_dict


def harvest():
    query = DBSession.query(Source)
    for source in query:
        response = requests.get(source.url)
        calendar = icalendar.Calendar.from_ical(response.text)
        for event_info in calendar.walk()[1:]:
            uid = event_info['uid']
            if DBSession.query(Event).filter_by(uid=uid).count():
                continue
            event = Event(**icalendar_to_event_dict(event_info))
            DBSession.add(event)
    DBSession.flush()
