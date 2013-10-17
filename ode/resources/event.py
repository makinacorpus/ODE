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
        """Add a new event"""
        event_info = json.loads(self.request.body)
        event = Event(**event_info)
        DBSession.add(event)
        DBSession.flush()
        return {'id': event.id, 'status': 'created'}

    @view(schema=EventSchema)
    def put(self):
        """Update existing event"""
        event_id = self.request.matchdict['id']
        query = DBSession.query(Event).filter_by(id=event_id)
        query.update(self.request.validated)
        return {'status': 'updated'}

    def collection_get(self):
        query = DBSession.query(Event).all()
        events = [event.json_data() for event in query]
        return {'events': events}

    def get(self):
        id = self.request.matchdict['id']
        event = DBSession.query(Event).filter_by(id=id).first()
        return {
            'status': 'success',
            'event': event.json_data(),
        }

    def delete(self):
        id = self.request.matchdict['id']
        event = DBSession.query(Event).filter_by(id=id).first()
        DBSession.delete(event)
        return {'status': 'deleted'}
