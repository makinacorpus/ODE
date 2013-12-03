# -*- encoding: utf-8 -*-
from unittest import TestCase
from mock import Mock, patch

from ode.models import Event, DBSession
from ode.tests.event import TestEventMixin
from ode.harvesting import harvest


valid_icalendar = u"""
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

start_time_missing = u"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AgendaDuLibre.org
X-WR-CALNAME:Agenda du Libre - tag toulibre
X-WR-TIMEZONE:Europe/Paris
CALSCALE:GREGORIAN
X-WR-CALDESC:L'Agenda des évènements autour du Libre, tag toulibre
BEGIN:VEVENT
DTEND;TZID=Europe/Paris:20121125T170000
UID:1234@example.com
SUMMARY:Capitole du Libre
URL:http://www.agendadulibre.org/showevent.php?id=7064
DESCRIPTION:Un évènement de l'Agenda du Libre
LOCATION:Toulouse
END:VEVENT
END:VCALENDAR
"""


class TestHarvesting(TestEventMixin, TestCase):

    def setup_requests_mock(self, icalendar_data=valid_icalendar):
        requests_patcher = patch('ode.harvesting.requests')
        self.mock_requests = requests_patcher.start()
        self.addCleanup(requests_patcher.stop)
        self.mock_requests.get.return_value = Mock(
            content_type='text/calendar',
            text=icalendar_data,
        )

    def test_fetch_data_from_source(self):
        self.setup_requests_mock()
        source = self.make_source()
        harvest()
        self.mock_requests.get.assert_called_with(source.url)
        event = DBSession.query(Event).one()
        self.assertEqual(event.title, u"Capitole du Libre")
        self.assertEqual(event.url,
                         u"http://www.agendadulibre.org/showevent.php?id=7064")
        self.assertEqual(event.description,
                         u"Un évènement de l'Agenda du Libre")
        #self.assertEqual(event.locations[0].name, u"Toulouse")
        #self.assertEqual(event.locations[0].dates[0].start_time,
        #                 datetime(2012, 11, 24, 11))
        #self.assertEqual(event.locations[0].dates[0].end_time,
        #                 datetime(2012, 11, 25, 17))
        self.assertEqual(event.uid, u"1234@example.com")

    def test_duplicate_is_ignored(self):
        existing_event = self.create_event(
            title=u'Existing event',
            uid=u'1234@example.com',
        )
        DBSession.flush()
        self.setup_requests_mock()
        source = self.make_source()
        harvest()
        self.mock_requests.get.assert_called_with(source.url)
        event = DBSession.query(Event).one()
        self.assertEqual(event.title, existing_event.title)

    def test_invalid_calendar(self):
        self.setup_requests_mock(icalendar_data=start_time_missing)
        source = self.make_source()
        harvest()
        self.mock_requests.get.assert_called_with(source.url)
        self.assertEqual(DBSession.query(Event).count(), 0)
