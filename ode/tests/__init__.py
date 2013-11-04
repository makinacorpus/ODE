# -*- encoding: utf-8 -*-
from pyramid import testing
from webtest import TestApp

from ode import main
from ode.tests.support import initTestingDB
from ode.models import DBSession, Source


class BaseTestMixin(object):

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

    def make_source(self, url=u"http://example.com", owner_id='123'):
        source = Source(url=url, owner_id=owner_id)
        DBSession.add(source)
        DBSession.flush()
        return source
