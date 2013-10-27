from unittest import TestCase

from ode.models import DBSession, Source
from ode.tests import BaseTestMixin


class TestSource(BaseTestMixin, TestCase):

    def test_get_source(self):
        source = self.make_source()
        response = self.app.get('/sources/%s' % source.id)
        self.assertEqual(response.json['source']['url'], 'http://example.com')

    def test_delete_source(self):
        source = self.make_source()
        self.app.delete('/sources/%s' % source.id)
        count = DBSession.query(Source).count()
        self.assertEqual(count, 0)

    def test_create_source(self):
        sources_info = {'sources': [{'url': u'http://example.com/mysource'}]}
        self.app.post_json('/sources', sources_info)
        source = DBSession.query(Source).one()
        self.assertEqual(source.url, u'http://example.com/mysource')

    def test_update_source(self):
        source = self.make_source()
        response = self.app.put_json('/sources/%s' % source.id, {
            'url': 'http://example.com/myothersource',
        })
        self.assertEqual(response.json['status'], 'updated')

    def test_get_source_list(self):
        self.make_source(u"http://example.com/mysource")
        self.make_source(u"http://example.com/myothersource")
        response = self.app.get('/sources')
        self.assertEqual(len(response.json['sources']), 2)
