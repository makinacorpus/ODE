# -*- encoding: utf-8 -*-
from pyramid import testing
from webtest import TestApp as BaseTestApp

from ode import main
from ode.tests.support import initTestingDB
from ode.models import DBSession, Source


class TestApp(BaseTestApp):

    def get_json(self, url, status=200, headers={}):
        response = self.get(url, status=status, headers=headers)
        return response.json

    def delete_json(self, url, status=200, headers={}):
        response = self.delete(url, status=status, headers=headers)
        return response.json


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

    def make_source(self, url=u"http://example.com", provider_id='123'):
        source = Source(url=url, provider_id=provider_id)
        DBSession.add(source)
        DBSession.flush()
        return source

    def assertContains(self, response, string):
        self.assertIn(string, response.body.decode('utf-8'))

    def assertErrorMessage(self, response, message):
        for error in response.json['errors']:
            if message in error['description']:
                return
        raise AssertionError("Cannot find expected error message '%s'" %
                             message)

    def assertContentType(self, response, content_type):
        self.assertIn(content_type, response.headers['Content-Type'])
