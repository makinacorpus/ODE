# -*- encoding: utf-8 -*-
from datetime import datetime

from ode.tests import BaseTestMixin
from ode.models import DBSession, Event


class TestEventMixin(BaseTestMixin):

    def create_event(self, *args, **kwargs):
        for mandatory in ('start_time', 'end_time'):
            if mandatory not in kwargs:
                kwargs[mandatory] = datetime(2014, 1, 25, 15, 0)
        event = Event(**kwargs)
        DBSession.add(event)
        return event

    def assertContains(self, response, string):
        self.assertIn(string, response.body.decode('utf-8'))

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)
