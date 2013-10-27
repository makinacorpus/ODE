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
        """Delete a resource by id"""
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
        """Get a specific resource by id"""
        id = self.request.matchdict['id']
        try:
            resource = DBSession.query(self.model).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPNotFound()
        return {
            'status': 'success',
            self.name: resource.to_dict(),
        }

    def put(self):
        """Update an existing resource by id"""
        resouce_id = self.request.matchdict['id']
        query = DBSession.query(self.model).filter_by(id=resouce_id)
        if not query.update(self.request.validated):
            raise HTTPNotFound()
        return {'status': 'updated'}

    def collection_get(self):
        """Get list of resources"""
        query = DBSession.query(self.model).all()
        resources = [resource.to_dict() for resource in query]
        return {self.name_plural: resources}
