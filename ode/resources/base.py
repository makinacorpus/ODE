from sqlalchemy.orm.exc import NoResultFound

from ode.resources.exceptions import HTTPNotFound
from ode.models import DBSession


class ResourceMixin(object):

    def __init__(self, request):
        self.request = request

    @property
    def name(self):
        return self.model.__name__.lower()

    @property
    def name_plural(self):
        return self.name + 's'

    def delete(self):
        """Delete an object by id"""
        id = self.request.matchdict['id']
        try:
            event = DBSession.query(self.model).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPNotFound()
        DBSession.delete(event)
        return {'status': 'deleted'}

    def collection_post(self):
        """Add new resources"""
        resources_data = self.request.validated[self.name_plural]
        result_data = []
        for resource_data in resources_data:
            resource = self.model(**resource_data)
            DBSession.add(resource)
            DBSession.flush()
            result_data.append({'id': resource.id, 'status': 'created'})
        return {self.name_plural: result_data}

    def get(self):
        """Get a specific event by id"""
        id = self.request.matchdict['id']
        try:
            resource = DBSession.query(self.model).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPNotFound()
        return {
            'status': 'success',
            self.name: resource.to_dict(),
        }

