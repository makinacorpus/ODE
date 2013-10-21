# -*- encoding: utf-8 -*-
from unittest import TestCase
from datetime import datetime

from ode.models import DBSession
from ode.tests.event import TestEventMixin


class TestIcal(TestEventMixin, TestCase):

    def test_root(self):
        response = self.app.get('/', status=200)
        self.assertTrue('Pyramid' in response.body)

    def assertContains(self, response, string):
        self.assertIn(string, response.body.decode('utf-8'))

    def get_event(self, **kwargs):
        for mandatory in ('start_time', 'end_time'):
            if mandatory not in kwargs:
                kwargs[mandatory] = datetime(2014, 1, 25, 15, 0)
        event = self.create_event(**kwargs)
        DBSession.flush()

        response = self.app.get('/events/%s' % event.id,
                                headers={'Accept': 'text/calendar'})
        return event, response

    def test_content_type(self):
        event, response = self.get_event()
        self.assertEqual(response.content_type, 'text/calendar')

    def test_summary(self):
        event, response = self.get_event(title='A Title')
        self.assertContains(response, u'SUMMARY:%s' % event.title)

    def test_description(self):
        event, response = self.get_event(description='A description')
        self.assertContains(response,
                            u'DESCRIPTION:%s' % event.description.strip()[:10])

    def test_location(self):
        event, response = self.get_event(location_name='Location Name')
        self.assertContains(response,
                            u'LOCATION:%s' % event.location_name)

    def test_url(self):
        event, response = self.get_event(url='http://example.com/')
        self.assertContains(response, u'URL:%s' % event.url)

    def test_start_time(self):
        _, response = self.get_event(start_time=datetime(2013, 12, 25, 15, 0))
        self.assertContains(response, u'DTSTART;VALUE=DATE-TIME:20131225T1500')

    def test_end_time(self):
        _, response = self.get_event(end_time=datetime(2013, 12, 25, 15, 0))
        self.assertContains(response, u'DTEND;VALUE=DATE-TIME:20131225T1500')
