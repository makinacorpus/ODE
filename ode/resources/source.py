from cornice.resource import resource, view

from ode.resources.exceptions import HTTPNotFound
from ode.models import Source, DBSession
from ode.resources.base import ResourceMixin
from ode.validation import SourceCollectionSchema
from ode.validation import SourceSchema
from ode.validation import has_producer_id


@resource(collection_path='/v1/sources', path='/v1/sources/{id}')
class SourceResource(ResourceMixin):

    model = Source

    @view(validators=[has_producer_id], schema=SourceCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)

    @view(validators=[has_producer_id], schema=SourceSchema)
    def put(self):
        """Update an existing resource by id"""
        resouce_id = self.request.matchdict['id']
        query = DBSession.query(self.model).filter_by(
            id=resouce_id,
            producer_id=self.request.validated['producer_id'],
        )
        data = self.request.validated
        data['url'] = data['url']['value']
        if not query.update(self.request.validated):
            raise HTTPNotFound()
        return {'status': 'updated'}
