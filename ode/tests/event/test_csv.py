# -*- encoding: utf-8 -*-
from unittest import TestCase
from StringIO import StringIO
import csv
from ode.models import DBSession

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
