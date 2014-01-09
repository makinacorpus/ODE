# -*- encoding: utf-8 -*-
from ode.tests import BaseTestMixin
from ode.models import DBSession, Event
from ode.deserializers import data_list_to_dict


class TestEventMixin(BaseTestMixin):

    def create_event(self, *args, **kwargs):

        event = Event(**kwargs)
        DBSession.add(event)
        return event

    def assertTitleEqual(self, event_id, title):
        event = DBSession.query(Event).filter_by(id=event_id).first()
        self.assertEqual(event.title, title)

    def post_event(self, event_info=None, headers=None):
        if headers is None:
            headers = {'X-ODE-Provider-Id': '123'}
        if event_info is None:
            event_info = [
                {'name': 'title', 'value': u'Titre Événement'},
            ]
        for mandatory in ('start_time', 'end_time', 'publication_start',
                          'publication_end'):
            if mandatory not in [field['name'] for field in event_info]:
                event_info.append({
                    'name': mandatory,
                    'value': '2014-01-25T15:00:00',
                })

        body_data = {
            'template': {
                'data': event_info
            }
        }
        created = 201
        headers['content-type'] = 'application/vnd.collection+json'
        response = self.app.post_json('/v1/events', body_data,
                                      headers=headers,
                                      status=created)
        data_dict = data_list_to_dict(
            response.json['collection']['items'][0]['data'])
        return data_dict['id']
