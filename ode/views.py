from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name='home', renderer='string')
def my_view(request):
    return HTTPFound('https://ode.readthedocs.org')
