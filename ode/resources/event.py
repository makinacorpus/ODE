from cornice.resource import resource, view

from ode.models import Event
from ode.validation import EventSchema, EventCollectionSchema, has_owner
from ode.resources.base import ResourceMixin


@resource(collection_path='/v1/events', path='/v1/events/{id}')
class EventResource(ResourceMixin):

    model = Event

    @view(validators=[has_owner], schema=EventCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)

    @view(validators=[has_owner], schema=EventSchema)
    def put(self):
        return ResourceMixin.put(self)

    @view(accept='text/calendar', renderer='ical')
    @view(accept='application/json', renderer='json')
    def collection_get(self):
        return ResourceMixin.collection_get(self)

    @view(accept='text/calendar', renderer='ical')
    @view(accept='application/json', renderer='json')
    def get(self):
        return ResourceMixin.get(self)
