# -*- encoding: utf-8 -*-
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
        event = Event(**kwargs)
        DBSession.add(event)
        return event

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)
