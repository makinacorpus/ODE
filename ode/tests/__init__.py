# -*- encoding: utf-8 -*-
import json

from pyramid import testing
from webtest import TestApp as BaseTestApp

from ode import main
from ode.tests.support import initTestingDB
from ode.models import DBSession, Source


class TestApp(BaseTestApp):

    def get_json(self, url, status=200):
        response = self.get(url, status=status)
        return json.loads(response.body)


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

    def make_source(self, url=u"http://example.com", producer_id='123'):
        source = Source(url=url, producer_id=producer_id)
        DBSession.add(source)
        DBSession.flush()
        return source

    def assertErrorMessage(self, response, message):
        for error in response.json['errors']:
            if message in error['description']:
                return
        raise AssertionError("Cannot find expected error message '%s'" %
                             message)

