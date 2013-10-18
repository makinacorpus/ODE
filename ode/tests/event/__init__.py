# -*- encoding: utf-8 -*-
from webtest import TestApp

from ode import main
from ode.tests.support import initTestingDB
from ode.models import DBSession, Event


class TestEventMixin(object):

    example_data = {
        'address': '10 rue des Roses',
        'audio_license': 'CC',
        'audio_url': 'http://example.com/audio',
        'author_email': 'bob@example.com',
        'author_firstname': u'François',
        'author_lastname': u'Vittsjö',
        'author_telephone': '000-999-23-30',
        'country': u'日本',
        'post_code': 'UVH-345',
        'description': u'''
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a
        diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac
        quam viverra nec consectetur ante hendrerit. Donec et mollis dolor.
        Praesent et diam eget libero egestas mattis sit amet vitae
        augue.''',
        'event_id': 'abc123',
        'email': 'alice@example.com',
        'firstname': 'Alice',
        'language': u'Français',
        'lastname': u'Éléonore',
        'latlong': u"1.0;2.0",
        'location_name': u'Nîmes',
        'organiser': u'LiberTIC',
        'capacity': u'42',
        'price_information': u'Plutôt bon marché',
        'performers': u'Basile Dupont;José Durand',
        'photos1_license': u'License Info 1',
        'photos1_url': u'http://example.com/photo1',
        'photos2_license': u'License Info 2',
        'photos2_url': u'http://example.com/photo2',
        'press_url': u'http://example.com/photo2',
        'source_id': u'xyz123',
        'source': u'http://example.com/event-source',
        'target': u'all',
        'telephone': u'1234567890',
        'title': u'Convention des amis des éléphants',
        'town': u'上海',
        'video_license': u'Video License Info',
        'video_url': 'http://example.com/video',
    }

    def setUp(self):
        settings = {'sqlalchemy.url': 'sqlite://'}
        app = main({}, **settings)
        self.app = TestApp(app)
        initTestingDB()

    def tearDown(self):
        del self.app
        DBSession.remove()

    def create_event(self, *args, **kwargs):
        event = Event(**kwargs)
        DBSession.add(event)
        return event

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)
