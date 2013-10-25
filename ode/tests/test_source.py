from unittest import TestCase

from ode.models import DBSession, Source
from ode.tests import BaseTestMixin


class TestSource(BaseTestMixin, TestCase):

    def test_get_source(self):
        source = Source(url="http://example.com")
        DBSession.add(source)
        DBSession.flush()
        source_id = source.id
        response = self.app.get('/sources/%s' % source_id)
        self.assertEqual(response.json['source']['url'], 'http://example.com')
