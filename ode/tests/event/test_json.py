# -*- encoding: utf-8 -*-
from unittest import TestCase

from ode.models import DBSession, Event
from ode.tests.event import TestEventMixin


class TestJson(TestEventMixin, TestCase):

    def test_root(self):
        response = self.app.get('/', status=200)
        self.assertTrue('Pyramid' in response.body)

    def post_event(self, event_info=None):
        if event_info is None:
            event_info = {'title': u'Titre Événement'}
        response = self.app.post_json('/events', event_info)
        return response.json['id']

    def test_post_event(self):
        event_id = self.post_event()
        self.assertTitleEqual(event_id, u'Titre Événement')

    def test_post_title_too_long(self):
        very_long_title = '*' * 1001
        response = self.app.post_json('/events', {
            'title': very_long_title
        }, status=400)
        self.assertEqual(response.json['status'], 'error')

    def test_update_event(self):
        event_id = self.post_event()
        response = self.app.put_json('/events/%s' % event_id, {
            'title': 'EuroPython',
        })
        self.assertTitleEqual(event_id, 'EuroPython')
        self.assertEqual(response.json['status'], 'updated')

    def test_update_title_too_long(self):
        event_id = self.post_event()
        very_long_title = '*' * 1001
        response = self.app.put_json('/events/%s' % event_id, {
            'title': very_long_title
        }, status=400)
        self.assertEqual(response.json['status'], 'error')

    def test_list_events(self):
        self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        response = self.app.get('/events')
        events = response.json['events']
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['title'], u'Événement 1')

    def test_get_event(self):
        id = self.post_event()
        response = self.app.get('/events/%s' % id)
        self.assertEqual(response.json['event']['title'],
                         u'Titre Événement')

    def test_delete_event(self):
        id = self.post_event()
        self.app.delete('/events/%s' % id)
        self.assertEqual(DBSession.query(Event).count(), 0)

    def test_post_all_fields(self):
        event_id = self.post_event(self.example_data)
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertDictEqual(event.json_data(), self.example_data)

    def test_get_all_fields(self):
        event = self.create_event(**self.example_data)
        DBSession.flush()
        response = self.app.get('/events/%s' % event.id)
        self.assertDictEqual(response.json['event'], self.example_data)

    def test_get_invalid_id(self):
        response = self.app.get('/events/42', status=404)
        self.assertEqual(response.json['status'], 404)

    def test_put_invalid_id(self):
        response = self.app.put('/events/42', status=404)
        self.assertEqual(response.json['status'], 404)

    def test_delete_invalid_id(self):
        response = self.app.delete('/events/42', status=404)
        self.assertEqual(response.json['status'], 404)
