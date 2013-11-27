import icalendar
import requests
from colander import Invalid

from ode.models import DBSession, Source, Event
from ode.resources.base import ResourceMixin
from ode.validation import EventSchema
from deserializers import icalendar_to_cstruct


def exists(uid):
    return DBSession.query(Event).filter_by(uid=uid).count() > 0


def validate(icalendar_event):
    cstruct = icalendar_to_cstruct(icalendar_event)
    schema = EventSchema()
    return schema.deserialize(cstruct)


def harvest():
    query = DBSession.query(Source)
    for source in query:
        response = requests.get(source.url)
        calendar = icalendar.Calendar.from_ical(response.text)
        for icalendar_event in calendar.walk()[1:]:
            uid = icalendar_event['uid']
            if not exists(uid):
                try:
                    model_kwargs = validate(icalendar_event)
                except Invalid:
                    continue
                model_kwargs = ResourceMixin.flatten_values(model_kwargs)
                event = Event(**model_kwargs)
                DBSession.add(event)
    DBSession.flush()
