# -*- encoding: utf-8 -*-
from unittest import TestCase
from mock import Mock, patch
from datetime import datetime

from ode.models import Event, DBSession
from ode.tests.event import TestEventMixin
from ode.harvesting import harvest


icalendar_example = u"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AgendaDuLibre.org
X-WR-CALNAME:Agenda du Libre - tag toulibre
X-WR-TIMEZONE:Europe/Paris
CALSCALE:GREGORIAN
X-WR-CALDESC:L'Agenda des évènements autour du Libre, tag toulibre
BEGIN:VEVENT
DTSTART;TZID=Europe/Paris:20121124T110000
DTEND;TZID=Europe/Paris:20121125T170000
UID:1234@example.com
SUMMARY:Capitole du Libre
URL:http://www.agendadulibre.org/showevent.php?id=7064
DESCRIPTION:Un évènement de l'Agenda du Libre
LOCATION:Toulouse
END:VEVENT
END:VCALENDAR
"""


@patch('ode.harvesting.requests')
class TestSource(TestEventMixin, TestCase):

    def test_fetch_data_from_source(self, mock_requests):
        mock_requests.get.return_value = Mock(
            content_type='text/calendar',
            text=icalendar_example,
        )
        source = self.make_source()
        harvest()
        mock_requests.get.assert_called_with(source.url)
        event = DBSession.query(Event).one()
        self.assertEqual(event.title, u"Capitole du Libre")
        self.assertEqual(event.url,
                         u"http://www.agendadulibre.org/showevent.php?id=7064")
        self.assertEqual(event.description,
                         u"Un évènement de l'Agenda du Libre")
        self.assertEqual(event.location_name, u"Toulouse")
        self.assertEqual(event.uid, u"1234@example.com")
        self.assertEqual(event.start_time, datetime(2012, 11, 24, 11))
        self.assertEqual(event.end_time, datetime(2012, 11, 25, 17))

    def test_duplicate_is_ignored(self, mock_requests):
        existing_event = self.create_event(
            title=u'Existing event',
            uid=u'1234@example.com',
        )
        DBSession.flush()

        mock_requests.get.return_value = Mock(
            content_type='text/calendar',
            text=icalendar_example,
        )
        source = self.make_source()
        harvest()
        mock_requests.get.assert_called_with(source.url)
        event = DBSession.query(Event).one()
        self.assertEqual(event.title, existing_event.title)
