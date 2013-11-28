from cornice.resource import resource, view

from ode.models import Event
from ode.models import DBSession, flatten_values
from ode.validation import EventSchema, EventCollectionSchema, has_producer_id
from ode.resources.base import ResourceMixin
from ode.resources.exceptions import HTTPNotFound
from ode.validation import validate_querystring


@resource(collection_path='/v1/events', path='/v1/events/{id}')
class EventResource(ResourceMixin):

    model = Event

    @view(validators=[has_producer_id], schema=EventCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)

    @view(validators=[has_producer_id], schema=EventSchema)
    def put(self):
        """Update an existing resource by id"""
        resouce_id = self.request.matchdict['id']
        query = DBSession.query(self.model).filter_by(
            id=resouce_id,
            producer_id=self.request.validated['producer_id'],
        )
        self.request.validated['producer_id'] = {
            'value': self.request.validated['producer_id']
        }
        data = flatten_values(self.request.validated)
        if 'locations' in data:
            locations = data.pop('locations')
        event = query.first()
        if not event:
            raise HTTPNotFound()
        event.set_locations(locations)
        query.update(data)
        return {'status': 'updated'}

    @view(accept='text/calendar', renderer='ical',
          validators=[validate_querystring])
    @view(accept='application/json', renderer='json',
          validators=[validate_querystring])
    def collection_get(self):
        return ResourceMixin.collection_get(self)

    @view(accept='text/calendar', renderer='ical')
    @view(accept='application/json', renderer='json')
    def get(self):
        return ResourceMixin.get(self)
