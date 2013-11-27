from sqlalchemy.orm.exc import NoResultFound
from cornice.resource import view

from ode.resources.exceptions import HTTPNotFound, HTTPBadRequest
from ode.models import DBSession, flatten_values
from ode.validation import has_producer_id
from ode.validation import validate_querystring


class ResourceMixin(object):

    def __init__(self, request):
        self.request = request

    @property
    def name(self):
        return self.model.__name__.lower()

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

    @staticmethod
    def flatten_values(mapping):
        mapping = flatten_values(mapping)
        if 'locations' in mapping:
            locations = mapping['locations']
            for i, location in enumerate(locations):
                locations[i] = flatten_values(location)
                for j, date in enumerate(locations[i]['dates']):
                    locations[i]['dates'][j] = flatten_values(
                        locations[i]['dates'][j])
        return mapping

    def collection_post(self):
        """Add new resources"""
        collection = self.request.validated['collection']
        items = collection['items']
        producer_id = self.request.validated['producer_id']
        result_items = []
        for item in items:
            item_data = self.flatten_values(item['data'])
            item_data['producer_id'] = producer_id
            resource = self.model(**item_data)
            DBSession.add(resource)
            DBSession.flush()
            result_items.append({
                'data': {'id': {'value': resource.id}},
                'status': 'created',
            })
        return {
            'collection': {
                'items': result_items
            }
        }

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
