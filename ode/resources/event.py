from cornice.resource import resource, view
import json

from ode.models import DBSession, Event
from ode.validation import EventSchema


@resource(collection_path='/events', path='/events/{id}')
class EventResource(object):

    def __init__(self, request):
        self.request = request

    @view(schema=EventSchema)
    def collection_post(self):
        event_info = json.loads(self.request.body)
        event = Event(**event_info)
        DBSession.add(event)
        DBSession.flush()
        return {'id': event.id, 'status': 'added'}

    @view(schema=EventSchema)
    def collection_put(self):
        event_info = json.loads(self.request.body)
        event = DBSession.query(Event).filter_by(id=event_info['id']).first()
        event.title = event_info['title']
        DBSession.add(event)

    def collection_get(self):
        query = DBSession.query(Event).all()
        events = [{'title': event.title} for event in query]
        return {'events': events}

    def get(self):
        id = self.request.matchdict['id']
        event = DBSession.query(Event).filter_by(id=id).first()
        return {'title': event.title}

    def delete(self):
        id = self.request.matchdict['id']
        event = DBSession.query(Event).filter_by(id=id).first()
        DBSession.delete(event)
        return {'status': 'deleted'}
