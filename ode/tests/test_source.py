from unittest import TestCase

from ode.models import DBSession, Source
from ode.tests import BaseTestMixin


class TestSource(BaseTestMixin, TestCase):

    def test_get_source(self):
        source = self.make_source()
        response = self.app.get('/v1/sources/%s' % source.id)
        self.assertEqual(response.json['source']['url'], 'http://example.com')

    def test_delete_source(self):
        source = self.make_source(producer_id=123)
        self.app.delete('/v1/sources/%s' % source.id,
                        headers={'X-ODE-Producer-Id': '123'})
        count = DBSession.query(Source).count()
        self.assertEqual(count, 0)

    def test_anonymous_cannot_delete(self):
        source = self.make_source()
        self.app.delete('/v1/sources/%s' % source.id, status=403)
        count = DBSession.query(Source).count()
        self.assertEqual(count, 1)

    def test_other_people_stuff(self):
        source = self.make_source(producer_id='abc')
        self.app.delete('/v1/sources/%s' % source.id,
                        headers={'X-ODE-Producer-Id': '123'},
                        status=404)
        count = DBSession.query(Source).count()
        self.assertEqual(count, 1)

    def test_create_source(self):
        sources_info = {'sources': [{'url': u'http://example.com/mysource'}]}
        self.app.post_json('/v1/sources', sources_info, headers={
            'X-ODE-Producer-Id': '123'
        })
        source = DBSession.query(Source).one()
        self.assertEqual(source.url, u'http://example.com/mysource')

    def test_anonymous_cannot_create(self):
        sources_info = {'sources': [{'url': u'http://example.com/mysource'}]}
        self.app.post_json('/v1/sources', sources_info, status=403)
        self.assertEqual(DBSession.query(Source).count(), 0)

    def test_update_source(self):
        source = self.make_source()
        response = self.app.put_json(
            '/v1/sources/%s' % source.id,
            {'url': 'http://example.com/myothersource'},
            headers={'X-ODE-Producer-Id': '123'})
        self.assertEqual(response.json['status'], 'updated')

    def test_update_required_producer_id(self):
        source = self.make_source()
        self.app.put_json('/v1/sources/%s' % source.id, {'url': 'whatever'},
                          status=403)

    def test_cannot_update_other_people_stuff(self):
        source = self.make_source(producer_id='abc')
        response = self.app.put_json('/v1/sources/%s' % source.id,
                                     {'url': 'whatever'},
                                     status=404,
                                     headers={'X-ODE-Producer-Id': '123'})
        self.assertEqual(response.json['status'], 404)

    def test_get_source_list(self):
        self.make_source(u"http://example.com/mysource")
        self.make_source(u"http://example.com/myothersource")
        response = self.app.get('/v1/sources')
        self.assertEqual(len(response.json['sources']), 2)
