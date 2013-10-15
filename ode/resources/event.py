from cornice.resource import resource
import json

from ode.models import DBSession, Event


@resource(collection_path='/events', path='/events/{id}')
class EventResource(object):

    def __init__(self, request):
        self.request = request

    def collection_post(self):
        event_info = json.loads(self.request.body)
        event = Event(title=event_info['title'])
        DBSession.add(event)
        DBSession.flush()
        return {'id': event.id, 'status': 'added'}

    def collection_put(self):
        event_info = json.loads(self.request.body)
        event = DBSession.query(Event).filter_by(id=event_info['id']).first()
        event.title = event_info['title']
        DBSession.add(event)

    def collection_get(self):
        event = DBSession.query(Event).first()
        event_info = {'title': event.title}
        return [event_info]

    def get(self):
        id = self.request.matchdict['id']
        event = DBSession.query(Event).filter_by(id=id).first()
        return {'title': event.title}

    def delete(self):
        id = self.request.matchdict['id']
        event = DBSession.query(Event).filter_by(id=id).first()
        DBSession.delete(event)
        return {'status': 'deleted'}
