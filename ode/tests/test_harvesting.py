# -*- encoding: utf-8 -*-
from unittest import TestCase
from mock import Mock

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

uid_missing_domain_part = u"""
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
UID:1234
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

icalendar_with_timezone = u"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AgendaDuLibre.org
X-WR-CALNAME:Agenda du Libre - tag toulibre
X-WR-TIMEZONE:Europe/Paris
CALSCALE:GREGORIAN
X-WR-CALDESC:Whatever
BEGIN:VEVENT
DTSTART:20140120T180000Z
DTEND:20140120T210000Z
UID:1234@example.com
SUMMARY:Capitole du Libre
URL:http://www.exemple.org/foo
DESCRIPTION:Whatever
LOCATION:Toulouse
END:VEVENT
END:VCALENDAR
"""


valid_json = (
    u'{"collection": {"href": "http://localhost:6543/v1/events", "items": [{"h'
    u'ref": "http://localhost:6543/v1/events/4c81f072630e11e3953c5c260a0e691e%'
    u'40example.com", "data": [{"name": "id", "value": "4c81f072630e11e3953c5c'
    u'260a0e691e@example.com"}, {"name": "description", "value": "Description"'
    u'}, {"name": "performers", "value": "artiste1, artiste2, artiste3"}, {"na'
    u'me": "press_url", "value": "http://presse"}, {"name": "price_information'
    u'", "value": "tarif"}, {"name": "target", "value": "public"}, {"name": "t'
    u'itle", "value": "Test medias"}, {"name": "start_time", "value": "2013-12'
    u'-12T00:00:00"}, {"name": "end_time", "value": "2013-12-28T00:00:00"}, {"'
    u'name": "publication_start", "value": "2013-12-12T00:00:00"}, {"name": "p'
    u'ublication_end", "value": "2013-12-28T00:00:00"}, {"name": "press_contac'
    u't_email", "value": "aaa@aaa.aa"}, {"name": "press_contact_name", "value"'
    u': "nom presse"}, {"name": "press_contact_phone_number", "value": "teleph'
    u'one presse"}, {"name": "ticket_contact_email", "value": "aaa@aaa.aa"}, {'
    u'"name": "ticket_contact_name", "value": "nom billetterie"}, {"name": "ti'
    u'cket_contact_phone_number", "value": "telephone billetterie"}, {"name": '
    u'"location_name", "value": "Nom du lieu"}, {"name": "location_address", "'
    u'value": "Adresse du lieu"}, {"name": "location_post_code", "value": "Cod'
    u'e postal"}, {"name": "location_capacity", "value": "capacite"}, {"name":'
    u'"location_town", "value": "Ville"}, {"name": "location_country", "value"'
    u': "Pays"}, {"name": "tags", "value": ["tag1", "tag2", "tag3"]}, {"name":'
    u'"categories", "value": ["category1", "category2"]}, {"name": "images", "'
    u'value": [{"url": "http://photo", "license": "CC BY"}, {"url": "http://ph'
    u'oto2", "license": "CC BY"}]}, {"name": "videos", "value": [{"url": "http'
    u'://video", "license": "CC BY"}]}, {"name": "sounds", "value": [{"url": "'
    u'http://audio", "license": "CC BY"}]}]}], "current_count": 1, "version": '
    u'"1.0", "total_count": 1}}'
    )


class TestHarvesting(TestEventMixin, TestCase):

    def setup_requests_mock(self, content_type='text/calendar',
                            icalendar_data=valid_icalendar):
        self.mock_requests = self.patch('ode.harvesting.requests')
        self.mock_requests.get.return_value = Mock(
            status_code=200,
            content_type=content_type,
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

    def test_fetch_json_data_from_source(self):
        self.setup_requests_mock(content_type='text/json',
                                 icalendar_data=valid_json)
        source = self.make_source()
        harvest()
        self.mock_requests.get.assert_called_with(source.url)
        event = DBSession.query(Event).one()
        self.assertEqual(event.title, u"Test medias")
        self.assertEqual(event.description,
                         u"Description")

    def test_update_from_uid_missing_domain_part(self):
        self.create_event(title=u'Existing event', id=u'1234@example.com')
        DBSession.flush()
        self.setup_requests_mock(icalendar_data=uid_missing_domain_part)
        source = self.make_source()
        harvest()
        self.mock_requests.get.assert_called_with(source.url)
        event = DBSession.query(Event).one()
        self.assertEqual(event.title, u"Capitole du Libre")

    def test_update_from_uid_with_domain_part(self):
        self.create_event(title=u'Existing event', id=u'1234@example.com')
        DBSession.flush()
        self.setup_requests_mock(icalendar_data=valid_icalendar)
        source = self.make_source()
        harvest()
        self.mock_requests.get.assert_called_with(source.url)
        event = DBSession.query(Event).one()
        self.assertEqual(event.title, u"Capitole du Libre")

    def test_invalid_calendar(self):
        self.setup_requests_mock(icalendar_data=start_time_missing)
        source = self.make_source()
        harvest()
        self.mock_requests.get.assert_called_with(source.url)
        self.assertEqual(DBSession.query(Event).count(), 0)

    def test_fix_calendar_with_timezone_aware_datetimes(self):
        self.setup_requests_mock(icalendar_data=icalendar_with_timezone)
        self.make_source()
        harvest()
        harvest()  # Second call was crashing

    def test_bogus_data_does_not_crash_harvesting(self):
        log_mock = self.patch('ode.harvesting.log')
        source1 = self.make_source(url=u"http://example.com/a",
                                   provider_id='123')
        self.make_source(url=u"http://example.com/b", provider_id='456')
        self.setup_requests_mock()
        self.mock_requests.get.side_effect = [
            Mock(
                status_code=200,
                content_type='text/calendar',
                text='*** BOGUS DATA ***',
            ),
            Mock(
                status_code=200,
                content_type='text/calendar',
                text=valid_icalendar,
            ),
        ]
        harvest()
        self.assertEqual(DBSession.query(Event).count(), 1)
        log_mock.warning.assert_called_with(
            u"Failed to harvest source {} with URL {}".format(
                source1.id, source1.url),
            exc_info=True)
