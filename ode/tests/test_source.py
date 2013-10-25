from unittest import TestCase

from ode.models import DBSession, Source
from ode.tests import BaseTestMixin


class TestSource(BaseTestMixin, TestCase):

    def make_source(self):
        source = Source(url=u"http://example.com")
        DBSession.add(source)
        DBSession.flush()
        return source

    def test_get_source(self):
        source = self.make_source()
        response = self.app.get('/sources/%s' % source.id)
        self.assertEqual(response.json['source']['url'], 'http://example.com')

    def test_delete_source(self):
        source = self.make_source()
        self.app.delete('/sources/%s' % source.id)
        count = DBSession.query(Source).count()
        self.assertEqual(count, 0)
