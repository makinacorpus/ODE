# -*- encoding: utf-8 -*-
from datetime import datetime
from unittest import TestCase
from copy import deepcopy

from ode.models import DBSession, Event
from ode.tests.event import TestEventMixin


def remove_ids(dictionary):
    result = dict(dictionary)
    del result['id']
    del result['uid']
    return result


example_data = {
    "author_email": {'value': "bob@example.com"},
    "author_firstname": {'value': u"François"},
    "author_lastname": {'value': u"Vittsjö"},
    "author_telephone": {'value': "000-999-23-30"},
    "description": {'value': u"""
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a
    diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac
    quam viverra nec consectetur ante hendrerit. Donec et mollis dolor.
    Praesent et diam eget libero egestas mattis sit amet vitae
    augue."""},
    "event_id": {'value': "abc123"},
    "email": {'value': "alice@example.com"},
    "latlong": {'value': "1;3"},
    "firstname": {'value': "Alice"},
    "language": {'value': u"Français"},
    "lastname": {'value': u"Éléonore"},
    "organiser": {'value': u"LiberTIC"},
    "price_information": {'value': u"Plutôt bon marché"},
    "performers": {'value': u"Basile Dupont;José Durand"},
    "photos1_license": {'value': u"License Info 1"},
    "photos1_url": {'value': u"http://example.com/photo1"},
    "photos2_license": {'value': u"License Info 2"},
    "photos2_url": {'value': u"http://example.com/photo2"},
    "press_url": {'value': u"http://example.com/photo2"},
    "source_id": {'value': u"xyz123"},
    "source": {'value': u"http://example.com/event-source"},
    "target": {'value': u"all"},
    "telephone": {'value': u"1234567890"},
    "title": {'value': u"Convention des amis des éléphants"},
    "video_license": {'value': u"Video License Info"},
    "video_url": {'value': u"http://example.com/video"},
    "url": {'value': u"http://example.com/v1/events/covention-amis-elephant"},
    "locations": {
        'value': [
            {
                "name": {'value': u"Le café du commerce"},
                "address": {'value': "10 rue des Roses"},
                "country": {'value': u"日本"},
                "post_code": {'value': "UVH-345"},
                "town": {'value': u"上海"},
                "capacity": {'value': u"42"},
                "dates": {
                    'value': [
                        {
                            "start_time": {'value': datetime(2013, 12, 19, 9)},
                            "end_time": {'value': datetime(2013, 12, 19, 18)},
                        },
                        {
                            "start_time": {
                                'value': datetime(2013, 12, 20, 10)},
                            "end_time": {'value': datetime(2013, 12, 20, 14)},
                        },
                    ]
                }
            }
        ]
    },
    "sounds": {
        'value': [
            {
                "license": {'value': "CC By"},
                "url": {'value': "http://example.com/audio"},
            }
        ]
    }
}
example_json = deepcopy(example_data)
example_dates = example_json['locations']['value'][0]['dates']['value']
example_dates[0]['start_time']['value'] = "2013-12-19T09:00:00"
example_dates[0]['end_time']['value'] = "2013-12-19T18:00:00"
example_dates[1]['start_time']['value'] = "2013-12-20T10:00:00"
example_dates[1]['end_time']['value'] = "2013-12-20T14:00:00"


class TestJson(TestEventMixin, TestCase):
    maxDiff = None

    def post_event(self, event_info=None, headers=None, status=200):
        if headers is None:
            headers = {'X-ODE-Producer-Id': '123'}
        if event_info is None:
            event_info = {'title': {'value': u'Titre Événement'}}
        if not 'locations' in event_info:
            event_info['locations'] = example_json['locations']
        body_data = {
            'collection': {
                'items': [{'data': event_info}]
            }
        }
        response = self.app.post_json('/v1/events', body_data,
                                      headers=headers, status=status)
        return response.json['collection']['items'][0]['data']['id']['value']

    def make_locations_data(self, name, start_time):
        locations_data = deepcopy(example_json['locations'])
        location = locations_data['value'][0]
        location['name'] = {'value': name}
        date1 = location['dates']['value'][0]
        date1['start_time']['value'] = start_time
        return locations_data

    def assertEqualIgnoringId(self, result, expected):
        result = remove_ids(result)
        for key in result:
            if isinstance(result[key], dict):
                self.assertDictEqual(result[key], expected[key])
            else:
                self.assertEqual(result[key], expected[key])

    def test_root(self):
        response = self.app.get('/', status=302)
        self.assertTrue('ode' in response.body)

    def test_post_event(self):
        event_id = self.post_event()
        self.assertTitleEqual(event_id, u'Titre Événement')

    def test_post_event_with_invalid_producer_id(self):
        self.app.post_json('/v1/events', headers={'X-ODE-Producer-Id': '\n'},
                           status=403)

    def test_post_title_too_long(self):
        very_long_title = '*' * 1001
        response = self.app.post_json('/v1/events', {
            'collection': {
                'items': [
                    {'data': {'title': {'value': very_long_title}}}
                ]
            },
        }, status=400, headers={'X-ODE-Producer-Id': '123'})
        self.assertErrorMessage(response, 'Longer than maximum')

    def test_update_event(self):
        event_id = self.post_event()
        put_data = {
            'title': {'value': 'EuroPython'},
            'locations': self.make_locations_data(
                name=u'Évian',
                start_time="2013-12-19T10:00:00"
            )
        }

        response = self.app.put_json(
            '/v1/events/%s' % event_id, put_data,
            headers={'X-ODE-Producer-Id': '123'})

        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(response.json['status'], 'updated')
        self.assertEqual(event.title, 'EuroPython')
        self.assertEqual(event.locations[0].name, u"Évian")

    def test_update_title_too_long(self):
        event_id = self.post_event()
        very_long_title = '*' * 1001
        response = self.app.put_json('/v1/events/%s' % event_id, {
            'title': very_long_title
        }, headers={'X-ODE-Producer-Id': '123'}, status=400)
        self.assertEqual(response.json['status'], 'error')

    def test_list_events(self):
        self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        response = self.app.get('/v1/events')
        events = response.json['collection']['items']
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['data']['title']['value'], u'Événement 1')

    def test_list_limit(self):
        for i in range(1, 6):
            self.create_event(title=u'Événement %s' % i)

        response = self.app.get('/v1/events?limit=3')

        collection = response.json['collection']
        self.assertEqual(collection['total_count'], 5)
        events = collection['items']
        self.assertEqual(len(events), 3)

    def create_sortable_events(self):
        self.create_event(title=u'BBB')
        self.create_event(title=u'CCC')
        self.create_event(title=u'AAA')

    def test_default_order(self):
        self.create_sortable_events()

        response = self.app.get('/v1/events?sort_by=title')

        items = response.json['collection']['items']
        self.assertEqual(items[0]['data']['title']['value'], 'AAA')
        self.assertEqual(items[1]['data']['title']['value'], 'BBB')
        self.assertEqual(items[2]['data']['title']['value'], 'CCC')

    def test_descending_order(self):
        self.create_sortable_events()

        response = self.app.get(
            '/v1/events?sort_by=title&sort_direction=desc')

        items = response.json['collection']['items']
        self.assertEqual(items[0]['data']['title']['value'], 'CCC')
        self.assertEqual(items[1]['data']['title']['value'], 'BBB')
        self.assertEqual(items[2]['data']['title']['value'], 'AAA')

    def test_invalid_sort_direction(self):
        response = self.app.get(
            '/v1/events?sort_by=title&sort_direction=BOGUS',
            status=400)
        self.assertErrorMessage(response, 'not one of asc, desc')

    def test_invalid_order_field(self):
        response = self.app.get('/v1/events?sort_by=BOGUS',
                                status=400)
        self.assertErrorMessage(response, 'not a valid sorting')

    def test_order_with_limit(self):
        self.create_sortable_events()

        response = self.app.get('/v1/events?sort_by=title&limit=2')

        items = response.json['collection']['items']
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['data']['title']['value'], 'AAA')
        self.assertEqual(items[1]['data']['title']['value'], 'BBB')

    def test_get_event(self):
        id = self.post_event()
        response = self.app.get('/v1/events/%s' % id)
        self.assertEqual(response.json['event']['title']['value'],
                         u'Titre Événement')

    def test_delete_event(self):
        id = self.post_event()
        self.app.delete('/v1/events/%s' % id,
                        headers={'X-ODE-Producer-Id': '123'})
        self.assertEqual(DBSession.query(Event).count(), 0)

    def test_post_all_fields(self):
        event_id = self.post_event(example_json)
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqualIgnoringId(event.to_dict(), example_data)
        self.assertIn('@', event.uid)
        self.assertEqual(event.sounds[0].url, 'http://example.com/audio')
        self.assertEqual(event.sounds[0].license, 'CC By')

    def test_get_all_fields(self):
        event_id = self.post_event(example_json)
        DBSession.flush()
        response = self.app.get('/v1/events/%s' % event_id)
        self.assertEqualIgnoringId(response.json['event'], example_json)

    def test_get_invalid_id(self):
        response = self.app.get('/v1/events/42', status=404)
        self.assertEqual(response.json['status'], 404)

    def test_put_invalid_id(self):
        put_data = {
            u'title': {'value': u'Un événement'},
        }
        put_data['locations'] = example_json['locations']
        response = self.app.put_json(
            '/v1/events/42', put_data,
            headers={'X-ODE-Producer-Id': '123'}, status=404)
        self.assertEqual(response.json['status'], 404)

    def test_delete_invalid_id(self):
        response = self.app.delete('/v1/events/42', status=404,
                                   headers={'X-ODE-Producer-Id': '123'})
        self.assertEqual(response.json['status'], 404)
