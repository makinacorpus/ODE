from cornice.resource import resource, view

from ode.models import Event
from ode.validation.schema import EventCollectionSchema
from ode.validation.validators import validate_querystring, has_provider_id
from ode.resources.base import ResourceMixin


def set_content_type(response, request):
    if response.content_type == 'application/json':
        response.content_type = 'application/vnd.collection+json'


@resource(collection_path='/v1/events', path='/v1/events/{id}',
          filters=set_content_type)
class EventResource(ResourceMixin):

    model = Event

    @view(validators=[has_provider_id], schema=EventCollectionSchema,
          renderer='json')
    def collection_post(self):
        return ResourceMixin.collection_post(self)

    @view(validators=[has_provider_id], schema=EventCollectionSchema)
    def put(self):
        return ResourceMixin.put(self)

    @view(accept='text/calendar', renderer='ical',
          validators=[validate_querystring])
    @view(accept='text/csv', renderer='csv', validators=[validate_querystring])
    @view(accept=['', 'application/vnd.collection+json'], renderer='json',
          validators=[validate_querystring])
    def collection_get(self):
        return ResourceMixin.collection_get(self)

    @view(accept='text/calendar', renderer='ical')
    @view(accept='application/vnd.collection+json', renderer='json')
    def get(self):
        return ResourceMixin.get(self)
