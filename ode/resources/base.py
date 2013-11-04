from sqlalchemy.orm.exc import NoResultFound
from cornice.resource import view

from ode.resources.exceptions import HTTPNotFound
from ode.models import DBSession
from ode.validation import has_owner


class ResourceMixin(object):

    def __init__(self, request):
        self.request = request

    @property
    def name(self):
        return self.model.__name__.lower()

    @property
    def name_plural(self):
        return self.name + 's'

    @view(validators=[has_owner])
    def delete(self):
        """Delete a resource by id"""
        id = self.request.matchdict['id']
        try:
            event = DBSession.query(self.model).filter_by(
                id=id,
                owner_id=self.request.validated['owner_id'],
            ).one()
        except NoResultFound:
            raise HTTPNotFound()
        DBSession.delete(event)
        return {'status': 'deleted'}

    def collection_post(self):
        """Add new resources"""
        resources_data = self.request.validated[self.name_plural]
        owner_id = self.request.validated['owner_id']
        result_data = []
        for resource_data in resources_data:
            resource_data['owner_id'] = owner_id
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
        query = DBSession.query(self.model).filter_by(
            id=resouce_id,
            owner_id=self.request.validated['owner_id'],
        )
        if not query.update(self.request.validated):
            raise HTTPNotFound()
        return {'status': 'updated'}

    def collection_get(self):
        """Get list of resources"""
        query = DBSession.query(self.model).all()
        resources = [resource.to_dict() for resource in query]
        return {self.name_plural: resources}
