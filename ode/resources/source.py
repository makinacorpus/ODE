from cornice.resource import resource, view
from sqlalchemy.orm.exc import NoResultFound

from ode.models import DBSession, Source
from ode.resources.exceptions import HTTPNotFound
from ode.resources.base import ResourceMixin
from ode.validation import SourceCollectionSchema


@resource(collection_path='/sources', path='/sources/{id}')
class SourceResource(ResourceMixin):

    model = Source

    def get(self):
        """Get a specific event by id"""
        id = self.request.matchdict['id']
        try:
            event = DBSession.query(Source).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPNotFound()
        return {
            'status': 'success',
            'source': event.to_dict(),
        }

    @view(schema=SourceCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)
