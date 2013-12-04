from sqlalchemy.orm.exc import NoResultFound
from cornice.resource import view

from ode.resources.exceptions import HTTPNotFound, HTTPBadRequest
from ode.models import DBSession
from ode.validation import has_provider_id
from ode.validation import validate_querystring


class ResourceMixin(object):

    def __init__(self, request):
        self.request = request

    @property
    def name(self):
        return self.model.__name__.lower()

    @view(validators=[has_provider_id], renderer='no_content')
    def delete(self):
        """Delete a resource by id"""
        id = self.request.matchdict['id']
        try:
            event = DBSession.query(self.model).filter_by(
                id=id,
                provider_id=self.request.validated['provider_id'],
            ).one()
        except NoResultFound:
            raise HTTPNotFound()
        DBSession.delete(event)

    def collection_post(self):
        """Add new resources"""
        items = self.request.validated['items']
        provider_id = self.request.validated['provider_id']
        result_items = []
        for item in items:
            item['data']['provider_id'] = provider_id
            resource = self.model(**item['data'])
            DBSession.add(resource)
            DBSession.flush()
            result_items.append({
                'data': {'id': {'value': resource.id}},
                'status': 'created',
            })
        response = self.request.response
        response.status_code = 201
        if len(result_items) == 1:
            # POSTed a single item, we can send the Location header
            source_url = self.request.route_url(
                'sourceresource',
                id=result_items[0]['data']['id']['value'])
            response.headers['location'] = source_url
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
            'collection': {
                'items': [
                    {'data': resource.to_data_list()}
                ],
            }
        }

    @view(validators=[validate_querystring])
    def collection_get(self):
        """Get list of resources"""
        query = DBSession.query(self.model)
        if 'provider_id' in self.request.validated:
            query = query.filter_by(
                provider_id=self.request.validated['provider_id'])
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
        total_count = query.count()
        limit = self.request.validated.get('limit')
        if limit:
            query = query.limit(limit)
        offset = self.request.validated.get('offset')
        if offset:
            query = query.offset(offset)
        resources = [{"data": resource.to_data_list()}
                     for resource in query.all()]
        return {'collection': {
            'current_count': len(resources),
            'total_count': total_count,
            'items': resources,
        }}

    def put(self):
        """Update an existing resource by id"""
        resouce_id = self.request.matchdict['id']
        query = DBSession.query(self.model).filter_by(
            id=resouce_id,
            provider_id=self.request.validated['provider_id'],
        )
        self.request.validated['provider_id'] = {
            'value': self.request.validated['provider_id']
        }
        event = query.first()
        if not event:
            raise HTTPNotFound()
        event.update_from_appstruct(
            self.request.validated['items'][0]['data'])
        return {'status': 'updated'}
