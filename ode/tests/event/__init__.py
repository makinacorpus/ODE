# -*- encoding: utf-8 -*-
from datetime import datetime

from pyramid import testing
from webtest import TestApp

from ode import main
from ode.tests.support import initTestingDB
from ode.models import DBSession, Event


class TestEventMixin(object):

    def setUp(self):
        settings = {
            'sqlalchemy.url': 'sqlite://',
            'domain': 'example.com',
        }
        app = main({}, **settings)
        self.app = TestApp(app)
        testing.setUp(settings=settings)
        initTestingDB()

    def tearDown(self):
        del self.app
        DBSession.remove()
        testing.tearDown()

    def create_event(self, *args, **kwargs):
        for mandatory in ('start_time', 'end_time'):
            if mandatory not in kwargs:
                kwargs[mandatory] = datetime(2014, 1, 25, 15, 0)
        event = Event(**kwargs)
        DBSession.add(event)
        return event

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)

    def assertContains(self, response, string):
        self.assertIn(string, response.body.decode('utf-8'))
