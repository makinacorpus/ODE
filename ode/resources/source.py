from cornice.resource import resource, view

from ode.models import Source
from ode.resources.base import ResourceMixin
from ode.validation import SourceCollectionSchema
from ode.validation import SourceSchema
from ode.validation import has_producer_id
from ode.validation import validate_querystring


@resource(collection_path='/v1/sources', path='/v1/sources/{id}')
class SourceResource(ResourceMixin):

    model = Source

    @view(validators=[has_producer_id], schema=SourceCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)

    @view(validators=[has_producer_id], schema=SourceSchema)
    def put(self):
        return ResourceMixin.put(self)

    @view(validators=[has_producer_id, validate_querystring])
    def collection_get(self):
        return ResourceMixin.collection_get(self)
