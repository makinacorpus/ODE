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

    def test_root(self):
        response = self.app.get('/', status=200)
        self.assertTrue('Pyramid' in response.body)

    def post_event(self):
        response = self.app.post_json('/events', {'title': 'PyconFR'})
        return response.json['id']

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)

    def test_post_event(self):
        event_id = self.post_event()
        self.assertTitleEqual(event_id, 'PyconFR')

    def test_update_event(self):
        event_id = self.post_event()
        self.app.put_json('/events', {
            'id': event_id,
            'title': 'EuroPython',
        })
        self.assertTitleEqual(event_id, 'EuroPython')

    def test_list_events(self):
        self.post_event()
        response = self.app.get('/events')
        self.assertEqual(len(response.json), 1)

    def test_get_event(self):
        id = self.post_event()
        response = self.app.get('/events/%s' % id)
        self.assertEqual(response.json['title'], 'PyconFR')

    def test_delete_event(self):
        id = self.post_event()
        self.app.delete('/events/%s' % id)
        self.assertEqual(DBSession.query(Event).count(), 0)
