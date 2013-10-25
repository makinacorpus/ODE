from cornice.resource import resource, view

from ode.models import Source
from ode.resources.base import ResourceMixin
from ode.validation import SourceCollectionSchema
from ode.validation import SourceSchema


@resource(collection_path='/sources', path='/sources/{id}')
class SourceResource(ResourceMixin):

    model = Source

    @view(schema=SourceCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)

    @view(schema=SourceSchema)
    def put(self):
        return ResourceMixin.put(self)
