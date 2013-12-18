from sqlalchemy.orm.exc import NoResultFound
from cornice.resource import view

from ode.resources.exceptions import HTTPNotFound, HTTPBadRequest
from ode.models import DBSession
from ode.validation.schema import COLLECTION_MAX_LENGTH
from ode.validation.validators import has_provider_id
from ode.validation.validators import validate_querystring
from ode.urls import absolute_url


def set_content_type(response, request):
    if response.content_type == 'application/json':
        response.content_type = 'application/vnd.collection+json'


class ResourceMixin(object):

    def __init__(self, request):
        self.request = request
        self._ = self.request.translate

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
            resource = None
            if 'id' in item['data'].keys():
                resource = self.model.get_by_id(item['data']['id'])
                if resource is not None:
                    if provider_id != resource.provider_id:
                        self.request.response.status_code = 403
                        return self.collection_json(
                            [resource.to_item(self.request)]
                            )
                    resource.update_from_appstruct(item['data'])
                    DBSession.merge(resource)
            if resource is None:
                resource = self.model(**item['data'])
                DBSession.add(resource)
            DBSession.flush()
            result_items.append(resource.to_item(self.request))
        response = self.request.response
        response.status_code = 201
        if len(result_items) == 1:
            # POSTed a single item, we can send the Location header
            response.headers['location'] = result_items[0]['href']
        return self.collection_json(result_items)

    def get(self):
        """Get a specific resource by id"""
        id = self.request.matchdict['id']
        try:
            resource = DBSession.query(self.model).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPNotFound()
        items = [resource.to_item(self.request)]
        return self.collection_json(items)

    def collection_json(self, items):
        return {
            'collection': {
                'version': "1.0",
                'href': self.absolute_url(),
                'items': items,
            }
        }

    def absolute_url(self):
        route_name = 'collection_%sresource' % self.model.__name__.lower()
        return absolute_url(self.request, route_name)

    def collection_get_filter_query(self, query):
        if 'provider_id' in self.request.validated:
            query = query.filter_by(
                provider_id=self.request.validated['provider_id'])
        return query

    def collection_get_query(self):
        query = DBSession.query(self.model)
        query = self.collection_get_filter_query(query)
        sort_by = self.request.validated.get('sort_by')
        if sort_by:
            order_criterion = getattr(self.model, sort_by, None)
            if order_criterion:
                if self.request.validated['sort_direction'] == 'desc':
                    order_criterion = order_criterion.desc()
                query = query.order_by(order_criterion)
            else:
                message = self._(
                    u"${sort_by} is not a valid sorting criterion",
                    mapping={'sort_by': sort_by})
                raise HTTPBadRequest(message)
        total_count = query.count()
        limit = self.request.validated.get('limit', COLLECTION_MAX_LENGTH)
        query = query.limit(limit)
        offset = self.request.validated.get('offset')
        if offset:
            query = query.offset(offset)
        return (query, total_count)

    @view(validators=[validate_querystring])
    def collection_get(self):
        """Get list of resources"""
        query, total_count = self.collection_get_query()
        items = [resource.to_item(self.request) for resource in query.all()]
        result = self.collection_json(items)
        result['collection']['current_count'] = len(items)
        result['collection']['total_count'] = total_count
        return result

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
