# -*- encoding: utf-8 -*-
from datetime import datetime

from ode.tests import BaseTestMixin
from ode.models import DBSession, Event, Date, Location


class TestEventMixin(BaseTestMixin):

    def create_event(self, *args, **kwargs):

        if kwargs.get('end_time'):
            end_time = kwargs['end_time']
            del kwargs['end_time']
        else:
            end_time = datetime(2014, 1, 25, 15, 0)

        if kwargs.get('start_time'):
            start_time = kwargs['start_time']
            del kwargs['start_time']
        else:
            start_time = datetime(2014, 1, 25, 15, 0)

        if kwargs.get('location_name'):
            location = Location(name=kwargs['location_name'])
            del kwargs['location_name']
        else:
            location = Location()
        date = Date(start_time=start_time, end_time=end_time)
        location.dates.append(date)
        event = Event(**kwargs)
        event.locations.append(location)
        DBSession.add(event)
        return event

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)
