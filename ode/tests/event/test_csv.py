# -*- encoding: utf-8 -*-
from unittest import TestCase
from StringIO import StringIO
import csv
from ode.models import DBSession, Event

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

        reader = csv.DictReader(StringIO(response.body))

        self.assertIn('title', reader.fieldnames)

    def test_title(self):
        self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        DBSession.flush()

        response = self.app.get('/v1/events', headers={'Accept': 'text/csv'})

        reader = csv.DictReader(StringIO(response.body))
        row = reader.next()
        self.assertIn('title', row)
        self.assertEqual(row['title'].decode('utf-8'), u'Événement 1')


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
