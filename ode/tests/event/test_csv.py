# -*- encoding: utf-8 -*-
from datetime import datetime
from unittest import TestCase
import csv

from six import StringIO

from ode.models import DBSession, Event, Location, Tag, Sound
from ode.deserializers import csv_text
from ode.tests.event import TestEventMixin


class TestGetEvents(TestEventMixin, TestCase):

    def test_content_type(self):
        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})
        self.assertEqual(response.content_type, 'text/csv')

    def test_header(self):
        self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        DBSession.flush()

        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})

        reader = csv.DictReader(StringIO(response.text))

        self.assertIn('title', reader.fieldnames)

    def test_title(self):
        self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        DBSession.flush()

        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})

        reader = csv.DictReader(StringIO(csv_text(response.text)))
        row = next(reader)
        self.assertIn('title', row)
        self.assertEqual(row['title'], 'Événement 1')

    def test_random_fields(self):
        self.create_event(title=u'Événement 1', press_contact_name=u'Émile')
        self.create_event(title=u'Événement 2', description=u'Foo bar')
        DBSession.flush()

        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})

        reader = csv.DictReader(StringIO(csv_text(response.text)))
        row = next(reader)
        self.assertEqual(row['press_contact_name'], 'Émile')
        row = next(reader)
        self.assertEqual(row['description'], u'Foo bar')

    def test_location(self):
        self.create_event(title=u'Événement 1',
                          location=Location(name=u'Évian'))
        DBSession.flush()

        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})

        reader = csv.DictReader(StringIO(csv_text(response.text)))
        row = next(reader)
        self.assertEqual(row['location_name'], 'Évian')
        self.assertNotIn('location_event_id', row)

    def test_tags(self):
        event = self.create_event()
        event.tags = [Tag(name=u'Tag1'), Tag(name=u'Tag2')]
        DBSession.flush()

        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})
        reader = csv.DictReader(StringIO(response.text))
        row = next(reader)
        self.assertEqual(row['tags'], u'Tag1, Tag2')

    def test_sounds(self):
        event = self.create_event()
        event.sounds = [
            Sound(url=u'http://example.com/sound1', license='CC BY'),
            Sound(url=u'http://example.com/sound2', license='Whatever'),
        ]
        DBSession.flush()
        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})
        reader = csv.DictReader(StringIO(csv_text(response.text)))
        row = next(reader)
        self.assertEqual(row['sounds'],
                         u'http://example.com/sound1 (CC BY), '
                         + 'http://example.com/sound2 (Whatever)')

    def test_datetime(self):
        event = self.create_event()
        event.start_time = datetime(2014, 1, 25, 16)
        DBSession.flush()
        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})
        reader = csv.DictReader(StringIO(csv_text(response.text)))
        row = next(reader)
        self.assertEqual(row['start_time'], '2014-01-25T16:00:00')


class TestPostEvents(TestEventMixin, TestCase):

    def test_post(self):
        body_data = """title,description,start_time,end_time
Événement,A great event,2014-01-25T15:00,2014-01-25T19:00
Autre Événement,Another great event,2014-01-26T15:00,2014-01-26T19:00
"""
        self.app.post('/v1/events', body_data, status=201, headers={
            'Content-Type': 'text/csv',
            'X-ODE-Provider-Id': '123',
        })

        self.assertEqual(DBSession.query(Event).count(), 2)
        event = DBSession.query(Event).filter_by(title=u'Événement').one()
        self.assertEqual(event.description, u'A great event')

    def test_post_invalid(self):
        response = self.app.post('/v1/events', '*** BOGUS ***',
                                 status=400, headers={
                                     'Content-Type': 'text/csv',
                                     'X-ODE-Provider-Id': '123',
                                 })
        self.assertErrorMessage(response, 'Invalid CSV request body')

    def test_post_empty(self):
        response = self.app.post('/v1/events',
                                 status=400, headers={
                                     'Content-Type': 'text/csv',
                                     'X-ODE-Provider-Id': '123',
                                 })
        self.assertErrorMessage(response, 'Empty CSV request body')
