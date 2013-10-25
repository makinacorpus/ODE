from cornice.resource import resource, view
from sqlalchemy.orm.exc import NoResultFound

from ode.models import DBSession, Source
from ode.resources.exceptions import HTTPNotFound
from ode.resources.base import ResourceMixin
from ode.validation import SourceCollectionSchema


@resource(collection_path='/sources', path='/sources/{id}')
class SourceResource(ResourceMixin):

    model = Source

    @view(schema=SourceCollectionSchema)
    def collection_post(self):
        return ResourceMixin.collection_post(self)
