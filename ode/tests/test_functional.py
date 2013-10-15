from unittest import TestCase

from webtest import TestApp

from ode import main
from ode.tests.support import initTestingDB


class TestEventAPI(TestCase):

    def setUp(self):
        settings = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        self.testapp = TestApp(app)
        initTestingDB()

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue('Pyramid' in res.body)
