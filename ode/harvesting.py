import icalendar
import requests

from ode.models import DBSession, Source, Event


def harvest():
    query = DBSession.query(Source)
    for source in query:
        response = requests.get(source.url)
        calendar = icalendar.Calendar.from_ical(response.text)
        for event_info in calendar.walk()[1:]:
            uid = event_info['uid']
            if DBSession.query(Event).filter_by(uid=uid).count():
                continue
            event = Event(
                uid=uid,
                title=event_info['summary'],
                start_time=event_info['dtstart'].dt,
                url=event_info['url'],
                description=event_info['description'],
                location_name=event_info['location'],
                end_time=event_info['dtend'].dt,
            )
            DBSession.add(event)
