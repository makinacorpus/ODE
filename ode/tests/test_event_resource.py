# -*- encoding: utf-8 -*-
from unittest import TestCase

from webtest import TestApp

from ode import main
from ode.tests.support import initTestingDB
from ode.models import DBSession, Event


class TestEvent(TestCase):

    def setUp(self):
        settings = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        self.app = TestApp(app)
        initTestingDB()

    def tearDown(self):
        del self.app
        DBSession.remove()

    def test_root(self):
        response = self.app.get('/', status=200)
        self.assertTrue('Pyramid' in response.body)

    def post_event(self):
        response = self.app.post_json('/events', {'title': u'Titre Événement'})
        return response.json['id']

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)

    def create_event(self, title):
        event = Event(title=title)
        DBSession.add(event)

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
        self.app.put_json('/events', {
            'id': event_id,
            'title': 'EuroPython',
        })
        self.assertTitleEqual(event_id, 'EuroPython')

    def test_update_title_too_long(self):
        event_id = self.post_event()
        very_long_title = '*' * 1001
        response = self.app.put_json('/events', {
            'id': event_id,
            'title': very_long_title
        }, status=400)
        self.assertEqual(response.json['status'], 'error')

    def test_list_events(self):
        self.create_event(u'Événement 1')
        self.create_event(u'Événement 2')
        response = self.app.get('/events')
        events = response.json['events']
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['title'], u'Événement 1')

    def test_get_event(self):
        id = self.post_event()
        response = self.app.get('/events/%s' % id)
        self.assertEqual(response.json['title'], u'Titre Événement')

    def test_delete_event(self):
        id = self.post_event()
        self.app.delete('/events/%s' % id)
        self.assertEqual(DBSession.query(Event).count(), 0)
