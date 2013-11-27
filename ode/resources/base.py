from sqlalchemy.orm.exc import NoResultFound
from cornice.resource import view

from ode.resources.exceptions import HTTPNotFound, HTTPBadRequest
from ode.models import DBSession
from ode.validation import has_producer_id
from ode.validation import validate_querystring


class ResourceMixin(object):

    def __init__(self, request):
        self.request = request

    @property
    def name(self):
        return self.model.__name__.lower()

    @property
    def name_plural(self):
        return self.name + 's'

    @view(validators=[has_producer_id])
    def delete(self):
        """Delete a resource by id"""
        id = self.request.matchdict['id']
        try:
            event = DBSession.query(self.model).filter_by(
                id=id,
                producer_id=self.request.validated['producer_id'],
            ).one()
        except NoResultFound:
            raise HTTPNotFound()
        DBSession.delete(event)
        return {'status': 'deleted'}

    def collection_post(self):
        """Add new resources"""
        resources_data = self.request.validated[self.name_plural]
        producer_id = self.request.validated['producer_id']
        result_data = []
        for resource_data in resources_data:
            resource_data['producer_id'] = producer_id
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
            producer_id=self.request.validated['producer_id'],
        )
        if not query.update(self.request.validated):
            raise HTTPNotFound()
        return {'status': 'updated'}

    @view(validators=[validate_querystring])
    def collection_get(self):
        """Get list of resources"""
        query = DBSession.query(self.model)
        total_count = query.count()
        limit = self.request.validated.get('limit')
        if limit:
            query = query.limit(limit)
        offset = self.request.validated.get('offset')
        if offset:
            query = query.offset(offset)
        sort_by = self.request.validated.get('sort_by')
        if sort_by:
            order_criterion = getattr(self.model, sort_by, None)
            if order_criterion:
                if self.request.validated['sort_direction'] == 'desc':
                    order_criterion = order_criterion.desc()
                query = query.order_by(order_criterion)
            else:
                message = "{} is not a valid sorting criterion"
                raise HTTPBadRequest(message.format(sort_by))
        resources = [{"data": resource.to_dict()} for resource in query.all()]
        return {'collection': {
            'current_count': len(resources),
            'total_count': total_count,
            'items': resources,
        }}
