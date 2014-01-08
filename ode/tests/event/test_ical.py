# -*- encoding: utf-8 -*-
from unittest import TestCase
from datetime import datetime
from urllib import quote

import icalendar

from ode.models import DBSession, Event
from ode.tests.event import TestEventMixin


class TestGetEvent(TestEventMixin, TestCase):

    def get_event(self, **kwargs):
        event = self.create_event(**kwargs)
        DBSession.flush()

        response = self.app.get('/v1/events/%s' % event.id,
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
        self.assertEqual(event.location.name, 'Location Name')
        self.assertContains(response,
                            u'LOCATION:%s' % event.location.name)

    def test_url(self):
        event, response = self.get_event(url='http://example.com/')
        self.assertContains(response, u'URL:%s' % event.url)

    def test_start_time(self):
        _, response = self.get_event(start_time=datetime(2013, 12, 25, 15, 0))
        self.assertContains(response, u'DTSTART;VALUE=DATE-TIME:20131225T1500')

    def test_end_time(self):
        event, response = self.get_event(
            end_time=datetime(2013, 12, 25, 15, 0))
        self.assertEqual(event.end_time, datetime(2013, 12, 25, 15, 0))
        self.assertContains(response, u'DTEND;VALUE=DATE-TIME:20131225T1500')


class TestGetEventList(TestEventMixin, TestCase):

    def test_list_events(self):
        self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        response = self.app.get('/v1/events',
                                headers={'Accept': 'text/calendar'})
        self.assertContains(response, u'SUMMARY:Événement 1')
        self.assertContains(response, u'SUMMARY:Événement 2')


class TestPostEvent(TestEventMixin, TestCase):

    start_time = datetime(2013, 12, 25, 15, 0)
    end_time = datetime(2013, 12, 27, 15, 0)

    def make_icalendar(self, titles):
        calendar = icalendar.Calendar()
        for index, title in enumerate(titles):
            event = icalendar.Event()
            event.add('uid', '123-%s@example.com' % index)
            event.add('summary', title)
            event.add('dtstart', self.start_time)
            event.add('dtend', self.end_time)
            event.add('location', 'Toulouse')
            calendar.add_component(event)
        return calendar.to_ical()

    def post(self, calendar, status=201):
        return self.app.post('/v1/events', calendar, headers={
            'content-type': 'text/calendar',
            'X-ODE-Provider-Id': '123'
        }, status=status)

    def test_post_single_event(self):
        calendar = self.make_icalendar(titles=[u'Événement'])
        response = self.post(calendar)
        items = response.json['collection']['items']
        event = DBSession.query(Event).filter_by(title=u'Événement').one()
        self.assertEqual(items[0]['href'],
                         'http://localhost/v1/events/%s' % quote(event.id))

    def test_post_multiple_events(self):
        calendar = self.make_icalendar(titles=[u'Événement 1', u'Événement 2'])
        response = self.post(calendar)
        items = response.json['collection']['items']
        event = DBSession.query(Event).filter_by(title=u'Événement 1').one()
        self.assertEqual(items[0]['href'],
                         'http://localhost/v1/events/%s' % quote(event.id))

    def test_post_malformed_calendar(self):
        response = self.post('*** BOGUS ***', status=400)
        self.assertErrorMessage(response, 'Invalid iCalendar request body')
