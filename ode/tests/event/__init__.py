# -*- encoding: utf-8 -*-
from ode.tests import BaseTestMixin
from ode.models import DBSession, Event


class TestEventMixin(BaseTestMixin):

    def create_event(self, *args, **kwargs):

        event = Event(**kwargs)
        DBSession.add(event)
        return event

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)
