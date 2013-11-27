import pyramid
from sqlalchemy import (Column, Integer, Unicode, UnicodeText,
                        DateTime, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import relationship
from uuid import uuid1
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


SAFE_MAX_LENGTH = 1000


def default_column():
    return Column(Unicode(SAFE_MAX_LENGTH))


class ModelMixin(object):

    def to_dict(self):
        result = {}
        for column in self.__class__.__mapper__.columns:
            if column.name in ('producer_id', 'location_id', 'event_id'):
                continue
            if column.name == 'id' and self.__class__.__name__ != 'Event':
                continue
            result[column.name] = {'value': getattr(self, column.name)}
        for collection_name in ('locations', 'dates'):
            if hasattr(self, collection_name):
                result[collection_name] = {'value': []}
                collection = getattr(self, collection_name)
                for obj in collection:
                    result[collection_name]['value'].append(obj.to_dict())
        return result


class Event(ModelMixin, Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)

    audio_license = default_column()
    audio_url = default_column()
    author_email = default_column()
    author_firstname = default_column()
    author_lastname = default_column()
    author_telephone = default_column()
    description = Column(UnicodeText(SAFE_MAX_LENGTH))
    email = default_column()
    event_id = default_column()
    firstname = default_column()
    language = default_column()
    lastname = default_column()
    latlong = default_column()
    organiser = default_column()
    performers = default_column()
    photos1_license = default_column()
    photos1_url = default_column()
    photos2_license = default_column()
    photos2_url = default_column()
    press_url = default_column()
    price_information = default_column()
    source = default_column()
    source_id = default_column()
    target = default_column()
    telephone = default_column()
    title = default_column()
    uid = Column(Unicode(SAFE_MAX_LENGTH), unique=True)
    url = default_column()
    video_license = default_column()
    video_url = default_column()
    producer_id = default_column()

    locations = relationship('Location')

    def __init__(self, *args, **kwargs):
        if 'uid' not in kwargs:
            kwargs['uid'] = self.make_uid()
        locations = kwargs.get('locations', [])
        if locations:
            del kwargs['locations']
            for location_data in locations:
                dates = location_data.get('dates', [])
                location_kwargs = dict(location_data)
                del location_kwargs['dates']
                location = Location(**location_kwargs)
                self.locations.append(location)
                if dates:
                    del location_data['dates']
                    for date_data in dates:
                        date = Date(**date_data)
                        location.dates.append(date)
        super(Event, self).__init__(*args, **kwargs)

    def make_uid(self):
        return "{}@{}".format(
            uuid1().hex,
            pyramid.threadlocal.get_current_registry().settings['domain'],
        )


class Location(ModelMixin, Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)

    name = default_column()
    address = default_column()
    post_code = default_column()
    capacity = default_column()
    town = default_column()
    country = default_column()
    event_id = Column(Integer, ForeignKey('events.id'))
    dates = relationship('Date')


class Date(ModelMixin, Base):
    __tablename__ = 'dates'
    id = Column(Integer, primary_key=True)

    start_time = Column(DateTime(timezone=False))
    end_time = Column(DateTime(timezone=False))
    location_id = Column(Integer, ForeignKey('locations.id'))


class Source(ModelMixin, Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    url = default_column()
    producer_id = default_column()


icalendar_to_model_keys = {
    'uid': 'uid',
    'summary': 'title',
    'url': 'url',
    'description': 'description',
}


def flatten_values(mapping):
    result = {}
    for key, field in mapping.items():
        if field is None:
            continue
        else:
            result[key] = field['value']
    return result
