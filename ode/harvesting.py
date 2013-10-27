import icalendar
import requests

from ode.models import DBSession, Source, Event


def harvest():
    query = DBSession.query(Source)
    for source in query:
        response = requests.get(source.url)
        calendar = icalendar.Calendar.from_ical(response.text)
        for event_info in calendar.walk()[1:]:
            event = Event(
                title=event_info['summary'],
                start_time=event_info['dtstart'].dt,
            )
            DBSession.add(event)
