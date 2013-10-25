from sqlalchemy.orm.exc import NoResultFound

from ode.resources.exceptions import HTTPNotFound
from ode.models import DBSession


class ResourceMixin(object):

    def __init__(self, request):
        self.request = request

    def delete(self):
        """Delete an object by id"""
        id = self.request.matchdict['id']
        try:
            event = DBSession.query(self.model).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPNotFound()
        DBSession.delete(event)
        return {'status': 'deleted'}
