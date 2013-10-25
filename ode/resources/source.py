from cornice.resource import resource
from sqlalchemy.orm.exc import NoResultFound

from ode.models import DBSession, Source
from ode.resources.exceptions import HTTPNotFound


@resource(collection_path='/sources', path='/sources/{id}')
class SourceResource(object):

    def __init__(self, request):
        self.request = request

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
