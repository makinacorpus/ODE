from cornice.resource import resource, view

from ode.models import Source
from ode.resources.base import ResourceMixin
from ode.validation import SourceCollectionSchema
from ode.validation import SourceSchema
from ode.validation import has_owner


@resource(collection_path='/v1/sources', path='/v1/sources/{id}')
class SourceResource(ResourceMixin):

    model = Source

    @view(validators=[has_owner], schema=SourceCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)

    @view(validators=[has_owner], schema=SourceSchema)
    def put(self):
        return ResourceMixin.put(self)
