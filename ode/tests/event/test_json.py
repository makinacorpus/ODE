# -*- encoding: utf-8 -*-
from unittest import TestCase
from copy import deepcopy

from ode.models import DBSession, Event
from ode.tests.event import TestEventMixin
from ode.deserializers import data_list_to_dict


def remove_ids(fields):
    return [field for field in fields
            if field['name'] != 'id' and field['name'] != 'uid'
            and field['name'] != 'event_id']


example_data = [
    {'name': "author_email", 'value': "bob@example.com"},
    {'name': "author_firstname", 'value': u"François"},
    {'name': "author_lastname", 'value': u"Vittsjö"},
    {'name': "author_telephone", 'value': "000-999-23-30"},
    {'name': "description", 'value': u"""
     Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a
     diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac
     quam viverra nec consectetur ante hendrerit. Donec et mollis dolor.
     Praesent et diam eget libero egestas mattis sit amet vitae
     augue."""},
    {'name': "event_id", 'value': "abc123"},
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
    {'name': "url",
     'value': u"http://example.com/v1/events/covention-amis-elephant"},
    {'name': "tags", 'value': u"Jazz"},
    {'name': "tags", 'value': u"Classical"},
    {'name': "tags", 'value': u"Bourrée auvergnate"},
    {'name': "categories", 'value': u"Music"},
    {'name': "categories", 'value': u"音楽"},
    #{'name': "sounds",
    # 'value': [
    #     {'name': "license", 'value': "CC By"},
    #     {'name': "url", 'value': "http://example.com/audio"},
    # ]
    # },
    #{'name': "videos",
    # 'value': [
    #     {'name': "license", 'value': "CC By"},
    #     {'name': "url", 'value': "http://example.com/video"},
    # ]
    # },
    #{'name': "images",
    # 'value': [
    #     {'name': "license", 'value': "CC By"},
    #     {'name': "url", 'value': "http://example.com/image"},
    # ]
    # },
]
example_json = deepcopy(example_data)


class TestJson(TestEventMixin, TestCase):
    maxDiff = None

    def post_event(self, event_info=None, headers=None, status=200):
        if headers is None:
            headers = {'X-ODE-Provider-Id': '123'}
        if event_info is None:
            event_info = [
                {'name': 'title', 'value': u'Titre Événement'},
            ]
        for mandatory in ('start_time', 'end_time'):
            if mandatory not in [field['name'] for field in event_info]:
                event_info.append({
                    'name': mandatory,
                    'value': '2014-01-25T15:00',
                })

        body_data = {
            'template': {
                'data': event_info
            }
        }
        response = self.app.post_json('/v1/events', body_data,
                                      headers=headers, status=status)
        return response.json['collection']['items'][0]['data']['id']['value']

    def assertEqualIgnoringId(self, result, expected):
        result = remove_ids(result)
        self.assertEqual(dict(result), dict(expected))

    def test_root(self):
        response = self.app.get('/', status=302)
        self.assertTrue('ode' in response.body)

    def test_post_event(self):
        event_id = self.post_event()
        self.assertTitleEqual(event_id, u'Titre Événement')

    def test_post_event_with_invalid_provider_id(self):
        self.app.post_json('/v1/events',
                           headers={'X-ODE-Provider-Id': '\n'},
                           status=403)

    def test_post_title_too_long(self):
        very_long_title = '*' * 1001
        response = self.app.post_json('/v1/events', {
            'template': {
                'data': [
                    {'name': 'title', 'value': very_long_title}
                ]
            }
        }, status=400, headers={'X-ODE-Provider-Id': '123'})
        self.assertErrorMessage(response, 'Longer than maximum')

    def test_update_event(self):
        event_id = self.post_event()
        put_data = {
            'template': {
                'data': [
                    {'name': u'title', 'value': 'EuroPython'},
                    {'name': u'start_time', 'value': u'2014-01-25T15:00'},
                    {'name': u'end_time', 'value': u'2014-01-25T15:00'},
                ]
            }
        }

        response = self.app.put_json(
            '/v1/events/%s' % event_id, put_data,
            headers={'X-ODE-Provider-Id': '123'})

        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(response.json['status'], 'updated')
        self.assertEqual(event.title, 'EuroPython')
        #self.assertEqual(event.locations[0].name, u"Le café des artistes")

    def test_update_title_too_long(self):
        event_id = self.post_event()
        very_long_title = '*' * 1001
        response = self.app.put_json('/v1/events/%s' % event_id, {
            'title': very_long_title
        }, headers={'X-ODE-Provider-Id': '123'}, status=400)
        self.assertEqual(response.json['status'], 'error')

    def test_list_events(self):
        self.create_event(title=u'Événement 1')
        self.create_event(title=u'Événement 2')
        response = self.app.get('/v1/events')
        events = response.json['collection']['items']
        self.assertEqual(len(events), 2)
        self.assertEqual(self.get_item_title(events[0]), u'Événement 1')

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

    @staticmethod
    def get_item_title(item):
        return data_list_to_dict(item['data'])['title']['value']

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
        response = self.app.get('/v1/events/%s' % id)
        self.assertEqual(
            data_list_to_dict(response.json['event'])['title']['value'],
            u'Titre Événement')

    def test_delete_event(self):
        id = self.post_event()
        self.app.delete('/v1/events/%s' % id,
                        headers={'X-ODE-Provider-Id': '123'},
                        status=204)
        self.assertEqual(DBSession.query(Event).count(), 0)

    def test_post_all_fields(self):
        event_id = self.post_event(example_json)
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqualIgnoringId(event.to_data_list(), example_data)

    def test_uid(self):
        event_id = self.post_event(example_json)
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertIn('@', event.uid)

    def test_media(self):
        self.skipTest('todo')
        event_id = self.post_event(example_json)
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.sounds[0].url, 'http://example.com/audio')
        self.assertEqual(event.sounds[0].license, 'CC By')
        self.assertEqual(event.videos[0].url, 'http://example.com/video')
        self.assertEqual(event.images[0].url, 'http://example.com/image')

    def test_tags_and_categories(self):
        event_id = self.post_event(example_json)
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(len(event.tags), 3)
        self.assertEqual(event.tags[0].name, u"Jazz")
        self.assertEqual(event.tags[1].name, u"Classical")
        self.assertEqual(event.tags[2].name, u"Bourrée auvergnate")
        self.assertEqual(len(event.categories), 2)
        self.assertEqual(event.categories[0].name, u"Music")
        self.assertEqual(event.categories[1].name, u"音楽")

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
            'template': {
                'data': [
                    {'name': u'title', 'value': u'Un événement'},
                    {'name': u'start_time', 'value': '2014-01-25T15:00'},
                    {'name': u'end_time', 'value': '2014-01-25T15:00'},
                ]
            }
        }
        #put_data['locations'] = example_json['locations']
        response = self.app.put_json(
            '/v1/events/42', put_data,
            headers={'X-ODE-Provider-Id': '123'}, status=404)
        self.assertEqual(response.json['status'], 404)

    def test_delete_invalid_id(self):
        response = self.app.delete('/v1/events/42', status=404,
                                   headers={'X-ODE-Provider-Id': '123'})
        self.assertEqual(response.json['status'], 404)
