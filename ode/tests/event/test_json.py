# -*- encoding: utf-8 -*-
from unittest import TestCase
from datetime import datetime
import six
if six.PY3:
    from urllib.parse import quote
else:
    from urllib import quote

from ode.models import DBSession, Event, Tag, Image, Video, Sound
from ode.tests.event import TestEventMixin
from ode.deserializers import data_list_to_dict
from ode.validation.schema import COLLECTION_MAX_LENGTH
from ode.resources.base import COLLECTION_JSON_MIMETYPE


def remove_ids(fields):
    return [field for field in fields
            if field['name']
            not in ('id', 'provider_id', 'event_id',
                    'location_id', 'location_event_id')]


example_data = [
    {'name': "description", 'value': u"""
     Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a
     diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac
     quam viverra nec consectetur ante hendrerit. Donec et mollis dolor.
     Praesent et diam eget libero egestas mattis sit amet vitae
     augue."""},
    {'name': "email", 'value': "alice@example.com"},
    {'name': "latlong", 'value': "1;3"},
    {'name': "firstname", 'value': "Alice"},
    {'name': "language", 'value': u"Français"},
    {'name': "lastname", 'value': u"Éléonore"},
    {'name': "organiser", 'value': u"LiberTIC"},
    {'name': "price_information", 'value': u"Plutôt bon marché"},
    {'name': "performers", 'value': u"Basile Dupont;José Durand"},
    {'name': "press_url", 'value': u"http://example.com/photo2"},
    {'name': "source_id", 'value': u"xyz123"},
    {'name': "source", 'value': u"http://example.com/event-source"},
    {'name': "target", 'value': u"all"},
    {'name': "telephone", 'value': u"1234567890"},
    {'name': "title", 'value': u"Convention des amis des éléphants"},
    {'name': "url", 'value': u"http://example.com/foo/bar"},
]


class TestJson(TestEventMixin, TestCase):
    maxDiff = None

    def assertEqualIgnoringId(self, result, expected):
        result = remove_ids(result)
        self.assertEqual(data_list_to_dict(result),
                         data_list_to_dict(expected))

    def test_root(self):
        response = self.app.get('/', status=302)
        self.assertTrue(u'ode' in response.text)

    def test_post_event(self):
        event_id = self.post_event()
        self.assertTitleEqual(event_id, u'Titre Événement')

    def test_post_event_with_invalid_provider_id(self):
        self.app.post_json('/v1/events',
                           headers={
                               'X-ODE-Provider-Id': '\n',
                               'Content-Type': COLLECTION_JSON_MIMETYPE,
                           },
                           status=403)

    def test_post_title_too_long(self):
        very_long_title = '*' * 1001
        response = self.app.post_json('/v1/events', {
            'template': {
                'data': [
                    {'name': 'title', 'value': very_long_title}
                ]
            }
        }, status=400, headers=self.WRITE_HEADERS)
        self.assertErrorMessage(response, 'Longer than maximum')

    def test_post_malformed_json(self):
        response = self.app.post('/v1/events', '*** MALFORMED JSON ***',
                                 status=400, headers=self.WRITE_HEADERS)
        self.assertErrorMessage(response, 'Invalid JSON request body')

    def test_empty_json(self):
        response = self.app.post('/v1/events', status=400,
                                 headers=self.WRITE_HEADERS)
        self.assertErrorMessage(response, 'Empty JSON request body')

    def test_update_event(self):
        event_id = self.post_event()
        put_data = {
            'template': {
                'data': [
                    {'name': u'title', 'value': 'EuroPython'},
                    # Note we pass timezone aware datetimes to test
                    # that we'll drop the timezone properly
                    {'name': u'start_time', 'value': u'2014-01-25T09:00Z'},
                    {'name': u'end_time', 'value': u'2014-01-25T18:00Z'},
                    {'name': u'publication_start',
                     'value': u'2014-01-25T09:00Z'},
                    {'name': u'publication_end',
                     'value': u'2014-01-25T18:00Z'},
                ]
            }
        }

        response = self.app.put_json('/v1/events/%s' % event_id,
                                     put_data,
                                     headers=self.WRITE_HEADERS)

        event = Event.get_by_id(event_id)
        self.assertEqual(response.json['status'], 'updated')
        self.assertEqual(event.title, 'EuroPython')

    def test_update_title_too_long(self):
        event_id = self.post_event()
        very_long_title = '*' * 1001
        response = self.app.put_json('/v1/events/%s' % event_id, {
            'template': {
                'data': [
                    {'name': 'title', 'value': very_long_title},
                ],
            },
        }, headers=self.WRITE_HEADERS, status=400)
        self.assertEqual(response.json['status'], 'error')
        self.assertErrorMessage(response, 'Longer than maximum')

    def test_update_invalid_collecton_json(self):
        event_id = self.post_event()
        response = self.app.put_json('/v1/events/%s' % event_id, {
            'foo': 'bar',
        }, headers=self.WRITE_HEADERS, status=400)
        self.assertEqual(response.json['status'], 'error')
        self.assertErrorMessage(response, 'Invalid Collection+JSON input')

    def test_post_publication_times(self):
        response = self.app.post_json('/v1/events', {
            'template': {
                'data': [
                    {'name': 'title', 'value': u'Événement'},
                    {'name': u'start_time', 'value': u'2014-01-25T15:00'},
                    {'name': u'end_time', 'value': u'2014-01-25T15:00'},
                    {'name': 'publication_start',
                     'value': u'2014-01-25T16:00'},
                    {'name': 'publication_end', 'value': u'2014-01-25T17:00'},
                ]
            }
        }, headers=self.WRITE_HEADERS)
        event_data = data_list_to_dict(
            response.json['collection']['items'][0]['data'])
        event_id = event_data['id']
        event = Event.get_by_id(event_id)
        self.assertEqual(event.publication_start, datetime(2014, 1, 25, 16))
        self.assertEqual(event.publication_end, datetime(2014, 1, 25, 17))

    def test_post_contact_info(self):
        event_data = [
            {'name': 'title', 'value': u'Événement'},
            {'name': u'start_time', 'value': u'2014-01-25T15:00'},
            {'name': u'end_time', 'value': u'2014-01-25T15:00'},
            {'name': 'press_contact_name', 'value': u'Éléonore'},
            {'name': 'press_contact_email', 'value': u'foo@example.com'},
            {'name': 'press_contact_phone_number', 'value': u'123456789'},
            {'name': 'ticket_contact_name', 'value': u'Éléonore'},
            {'name': 'ticket_contact_email', 'value': u'bar@example.com'},
            {'name': 'ticket_contact_phone_number',
             'value': u'00000000'},
        ]
        event_id = self.post_event(event_data)
        event = Event.get_by_id(event_id)
        self.assertEqual(event.press_contact_name, u'Éléonore')
        self.assertEqual(event.press_contact_email, u'foo@example.com')
        self.assertEqual(event.ticket_contact_phone_number, u'00000000')

    def test_list_all_events(self):
        event1 = self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        response = self.app.get(
            '/v1/events',
            headers={
                'X-ODE-API-Mount-Point': 'http://example.com/api',
            })
        collection = response.json['collection']
        events = collection['items']
        self.assertEqual(len(events), 2)
        self.assertEqual(self.get_item_title(events[0]), u'Événement 1')
        self.assertEqual(
            events[0]['href'],
            'http://example.com/api/v1/events/%s' % quote(event1.id))
        self.assertEqual(collection['href'],
                         'http://example.com/api/v1/events')

    def test_list_provider_events(self):
        self.create_event(title=u'Événement 1', provider_id=42)
        self.create_event(title=u'Événement 2')
        response = self.app.get('/v1/events?provider_id=42')
        events = response.json['collection']['items']
        self.assertEqual(len(events), 1)
        self.assertEqual(self.get_item_title(events[0]), u'Événement 1')

    def test_default_limit(self):
        for i in range(0, COLLECTION_MAX_LENGTH + 1):
            self.create_event(title=u'Événement %s' % i)

        response = self.app.get('/v1/events')

        collection = response.json['collection']
        self.assertEqual(len(collection['items']), COLLECTION_MAX_LENGTH)
        self.assertEqual(collection['current_count'], COLLECTION_MAX_LENGTH)
        self.assertEqual(collection['total_count'], COLLECTION_MAX_LENGTH + 1)

    def test_client_limit(self):
        for i in range(1, 6):
            self.create_event(title=u'Événement %s' % i)

        response = self.app.get('/v1/events?limit=3')

        collection = response.json['collection']
        self.assertEqual(collection['total_count'], 5)
        events = collection['items']
        self.assertEqual(len(events), 3)

    def test_invalid_limit(self):
        for i in range(0, COLLECTION_MAX_LENGTH + 1):
            self.create_event(title=u'Événement %s' % i)

        url = '/v1/events?limit={}'.format(COLLECTION_MAX_LENGTH + 1)
        response = self.app.get(url, status=400)

        self.assertContentType(response, 'application/json')
        self.assertErrorMessage(response, 'greater than maximum')

    def create_sortable_events(self):
        self.create_event(title=u'BBB')
        self.create_event(title=u'CCC')
        self.create_event(title=u'AAA')

    @staticmethod
    def get_item_title(item):
        return data_list_to_dict(item['data'])['title']

    def test_default_order(self):
        self.create_sortable_events()

        response = self.app.get('/v1/events?sort_by=title')

        items = response.json['collection']['items']
        self.assertEqual(self.get_item_title(items[0]), 'AAA')
        self.assertEqual(self.get_item_title(items[1]), 'BBB')
        self.assertEqual(self.get_item_title(items[2]), 'CCC')

    def test_descending_order(self):
        self.create_sortable_events()

        response = self.app.get(
            '/v1/events?sort_by=title&sort_direction=desc')

        items = response.json['collection']['items']
        self.assertEqual(self.get_item_title(items[0]), 'CCC')
        self.assertEqual(self.get_item_title(items[1]), 'BBB')
        self.assertEqual(self.get_item_title(items[2]), 'AAA')

    def test_invalid_sort_direction(self):
        response = self.app.get(
            '/v1/events?sort_by=title&sort_direction=BOGUS',
            status=400)
        self.assertErrorMessage(response, 'not one of asc, desc')

    def test_ode_error_message_localization(self):
        response = self.app.get(
            '/v1/events?sort_by=BOGUS',
            status=400, headers={
                'Accept-Language': 'fr',
            })
        self.assertErrorMessage(response, u'pas un critère de tri valide')

    def test_colander_error_message_localization(self):
        response = self.app.get(
            '/v1/events?sort_by=title&sort_direction=BOGUS',
            status=400, headers={
                'Accept-Language': 'fr',
            })
        self.assertErrorMessage(response, u'ne fait pas partie des choix')

    def test_cornice_error_message_localization(self):
        very_long_title = '*' * 1001
        headers = dict(self.WRITE_HEADERS)
        headers['Accept-Language'] = 'fr'
        response = self.app.post_json('/v1/events', {
            'template': {
                'data': [
                    {'name': 'title', 'value': very_long_title}
                ]
            }
        }, status=400, headers=headers)
        self.assertErrorMessage(response, u'La longueur dépasse')

    def test_invalid_order_field(self):
        response = self.app.get('/v1/events?sort_by=BOGUS',
                                status=400)
        self.assertErrorMessage(response, 'not a valid sorting')

    def test_order_with_limit(self):
        self.create_sortable_events()

        response = self.app.get('/v1/events?sort_by=title&limit=2')

        items = response.json['collection']['items']
        self.assertEqual(len(items), 2)
        self.assertEqual(self.get_item_title(items[0]), 'AAA')
        self.assertEqual(self.get_item_title(items[1]), 'BBB')

    def test_get_event(self):
        id = self.post_event()

        response = self.app.get(
            '/v1/events/%s' % id,
            headers={'Accept': 'application/vnd.collection+json'})

        self.assertContentType(response, 'application/vnd.collection+json')
        event_data = response.json['collection']['items'][0]['data']
        event_dict = data_list_to_dict(event_data)
        title = event_dict['title']
        self.assertEqual(title, u'Titre Événement')

    def test_delete_event(self):
        id = self.post_event()
        self.app.delete('/v1/events/%s' % id,
                        headers=self.PROVIDER_ID_HEADER,
                        status=204)
        self.assertEqual(DBSession.query(Event).count(), 0)

    def test_all_fields(self):
        event_id = self.post_event(example_data)
        DBSession.flush()
        response = self.app.get(
            '/v1/events/%s' % event_id,
            headers={'Accept': 'application/vnd.collection+json'})
        event_data = response.json['collection']['items'][0]['data']
        self.assertEqualIgnoringId(event_data, example_data)

    def test_uid(self):
        event_id = self.post_event(example_data)
        event = Event.get_by_id(event_id)
        self.assertIn(event_id, event.id)

    def test_post_tags_and_categories(self):
        event_id = self.post_event([
            {'name': u'title', 'value': 'EuroPython'},
            {'name': "tags",
             'value': [u"Jazz", u"Classical", u"Bourrée auvergnate"]},
            {'name': "categories", 'value': [u"Music", u"音楽"]},
        ])

        event = Event.get_by_id(event_id)
        self.assertEqual(len(event.tags), 3)
        self.assertEqual(event.tags[0].name, u"Jazz")
        self.assertEqual(event.tags[1].name, u"Classical")
        self.assertEqual(event.tags[2].name, u"Bourrée auvergnate")
        self.assertEqual(len(event.categories), 2)
        self.assertEqual(event.categories[0].name, u"Music")
        self.assertEqual(event.categories[1].name, u"音楽")

    def test_get_tags(self):
        event = self.create_event()
        event.tags = [Tag(name=u'Music'), Tag(name=u"音楽")]
        DBSession.flush()
        response = self.app.get(
            '/v1/events/%s' % event.id,
            headers={'Accept': 'application/vnd.collection+json'})
        event_data = response.json['collection']['items'][0]['data']
        self.assertIn({'name': "tags", 'value': [u'Music', u"音楽"]},
                      event_data)

    def test_get_categories(self):
        event = self.create_event()
        event.categories = [Tag(name=u'Music'), Tag(name=u"音楽")]
        DBSession.flush()
        response = self.app.get(
            '/v1/events/%s' % event.id,
            headers={'Accept': 'application/vnd.collection+json'})
        event_data = response.json['collection']['items'][0]['data']
        self.assertIn({'name': "categories", 'value': [u'Music', u"音楽"]},
                      event_data)

    def _test_post_media(self, attrname):
        event_id = self.post_event([
            {'name': u'title', 'value': 'EuroPython'},
            {'name': attrname, "value": [
                {
                    "url": u"http://example.com/abc",
                    "license": u"CC By"
                },
                {
                    "url": u"http://example.com/123",
                    "license": u"Art Libre"
                }
            ]},
        ])
        event = Event.get_by_id(event_id)
        objects = getattr(event, attrname)
        self.assertEqual(len(objects), 2)
        self.assertEqual(objects[0].url, u"http://example.com/abc")
        self.assertEqual(objects[1].license, u"Art Libre")

    def test_post_images(self):
        self._test_post_media('images')

    def test_post_sounds(self):
        self._test_post_media('sounds')

    def test_post_videos(self):
        self._test_post_media('videos')

    def _test_get_media(self, klass):
        attrname = klass.__name__.lower() + 's'
        event = self.create_event()
        setattr(event, attrname, [
            klass(url=u'http://example.com/abc',
                  license=u'CC By'),
            klass(url=u'http://example.com/123',
                  license=u'Art Libre'),
        ])
        DBSession.flush()
        response = self.app.get(
            '/v1/events/%s' % event.id,
            headers={'Accept': 'application/vnd.collection+json'})
        event_data = response.json['collection']['items'][0]['data']
        self.assertIn(
            {'name': attrname, "value": [
                {
                    "url": u"http://example.com/abc",
                    "license": u"CC By"
                },
                {
                    "url": u"http://example.com/123",
                    "license": u"Art Libre"
                }
            ]},
            event_data)

    def test_get_images(self):
        self._test_get_media(Image)

    def test_get_videos(self):
        self._test_get_media(Video)

    def test_get_sounds(self):
        self._test_get_media(Sound)

    def test_get_invalid_id(self):
        response = self.app.get('/v1/events/42', status=404)
        self.assertEqual(response.json['status'], 404)

    def test_put_invalid_id(self):
        put_data = {
            'template': {
                'data': [
                    {'name': u'title', 'value': u'Un événement'},
                    {'name': u'start_time', 'value': '2014-01-25T15:00'},
                    {'name': u'end_time', 'value': '2014-01-25T15:00'},
                ]
            }
        }
        response = self.app.put_json('/v1/events/42', put_data,
                                     headers=self.WRITE_HEADERS, status=404)
        self.assertEqual(response.json['status'], 404)

    def test_delete_invalid_id(self):
        response = self.app.delete('/v1/events/42', status=404,
                                   headers={'X-ODE-Provider-Id': '123'})
        self.assertEqual(response.json['status'], 404)

    def test_start_time(self):
        self.post_event([
            {'name': u'title', 'value': u'Un événement'},
            {'name': u'start_time', 'value': '2014-01-25T15:00'},
            {'name': u'end_time', 'value': '2014-01-30T15:00'},
            ])
        response = self.app.get(
            '/v1/events?start_time=2014-01-27T15:00',
            headers={
                'X-ODE-API-Mount-Point': 'http://example.com/api',
            })
        collection = response.json['collection']
        events = collection['items']
        self.assertEqual(len(events), 1)
        response = self.app.get(
            '/v1/events?start_time=2014-02-01T15:00',
            headers={
                'X-ODE-API-Mount-Point': 'http://example.com/api',
            })
        collection = response.json['collection']
        events = collection['items']
        self.assertEqual(len(events), 0)

    def test_end_time(self):
        self.post_event([
            {'name': u'title', 'value': u'Un événement'},
            {'name': u'start_time', 'value': '2014-01-25T15:00'},
            {'name': u'end_time', 'value': '2014-01-30T15:00'},
            ])
        response = self.app.get(
            '/v1/events?end_time=2014-01-27T15:00',
            headers={
                'X-ODE-API-Mount-Point': 'http://example.com/api',
            })
        collection = response.json['collection']
        events = collection['items']
        self.assertEqual(len(events), 1)
        response = self.app.get(
            '/v1/events?end_time=2014-01-01T15:00',
            headers={
                'X-ODE-API-Mount-Point': 'http://example.com/api',
            })
        collection = response.json['collection']
        events = collection['items']
        self.assertEqual(len(events), 0)
