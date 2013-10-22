# -*- encoding: utf-8 -*-
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession, Base
from ode.deserializers import icalendar_extractor


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('cornice')
    config.include('ode.fainit')
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_renderer('ical', 'ode.renderers.IcalRenderer')
    config.add_renderer('json', 'ode.renderers.JsonRenderer')
    config.add_cornice_deserializer('text/calendar', icalendar_extractor)
    config.scan()
    return config.make_wsgi_app()
