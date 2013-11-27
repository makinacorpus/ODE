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
    "audio_license": "CC",
    "audio_url": "http://example.com/audio",
    "author_email": "bob@example.com",
    "author_firstname": u"François",
    "author_lastname": u"Vittsjö",
    "author_telephone": "000-999-23-30",
    "description": u"""
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a
    diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac
    quam viverra nec consectetur ante hendrerit. Donec et mollis dolor.
    Praesent et diam eget libero egestas mattis sit amet vitae
    augue.""",
    "event_id": "abc123",
    "email": "alice@example.com",
    "latlong": "1;3",
    "firstname": "Alice",
    "language": u"Français",
    "lastname": u"Éléonore",
    "organiser": u"LiberTIC",
    "price_information": u"Plutôt bon marché",
    "performers": u"Basile Dupont;José Durand",
    "photos1_license": u"License Info 1",
    "photos1_url": u"http://example.com/photo1",
    "photos2_license": u"License Info 2",
    "photos2_url": u"http://example.com/photo2",
    "press_url": u"http://example.com/photo2",
    "source_id": u"xyz123",
    "source": u"http://example.com/event-source",
    "target": u"all",
    "telephone": u"1234567890",
    "title": u"Convention des amis des éléphants",
    "video_license": u"Video License Info",
    "video_url": u"http://example.com/video",
    "url": u"http://example.com/v1/events/covention-amis-elephant",
    "locations": [
        {
            "name": u"Le café du commerce",
            "address": "10 rue des Roses",
            "country": u"日本",
            "post_code": "UVH-345",
            "town": u"上海",
            "capacity": u"42",
            "dates": [
                {
                    "start_time": datetime(2013, 12, 19, 9),
                    "end_time": datetime(2013, 12, 19, 18),
                },
                {
                    "start_time": datetime(2013, 12, 20, 10),
                    "end_time": datetime(2013, 12, 20, 14),
                },
            ]
        }
    ]
}
example_json = deepcopy(example_data)
example_dates = example_json['locations'][0]['dates']
example_dates[0]['start_time'] = "2013-12-19T09:00:00"
example_dates[0]['end_time'] = "2013-12-19T18:00:00"
example_dates[1]['start_time'] = "2013-12-20T10:00:00"
example_dates[1]['end_time'] = "2013-12-20T14:00:00"


class TestJson(TestEventMixin, TestCase):
    maxDiff = None

    def post_event(self, event_info=None, headers=None, status=200):
        if headers is None:
            headers = {'X-ODE-Producer-Id': '123'}
        if event_info is None:
            event_info = {'title': u'Titre Événement'}
        if not 'locations' in event_info:
            event_info['locations'] = example_json['locations']
        events_info = {'events': [event_info]}
        response = self.app.post_json('/v1/events', events_info,
                                      headers=headers, status=status)
        return response.json['events'][0]['id']

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
            'events': [{'title': very_long_title}],
        }, status=400, headers={'X-ODE-Producer-Id': '123'})
        self.assertErrorMessage(response, 'Longer than maximum')

    def test_update_event(self):
        event_id = self.post_event()
        put_data = {
            'title': 'EuroPython',
        }
        put_data['locations'] = example_json['locations']
        response = self.app.put_json('/v1/events/%s' % event_id, put_data,
                                     headers={'X-ODE-Producer-Id': '123'})
        self.assertTitleEqual(event_id, 'EuroPython')
        self.assertEqual(response.json['status'], 'updated')

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
        self.assertEqual(events[0]['data']['title'], u'Événement 1')

    def test_get_event(self):
        id = self.post_event()
        response = self.app.get('/v1/events/%s' % id)
        self.assertEqual(response.json['event']['title'],
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
            u'title': u'Un événement',
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
