import pyramid
from sqlalchemy import (Column, Integer, Unicode, UnicodeText,
                        DateTime, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import Table
from uuid import uuid1
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


SAFE_MAX_LENGTH = 1000
TAG_MAX_LENGTH = 50


def default_column():
    return Column(Unicode(SAFE_MAX_LENGTH))


class ModelMixin(object):

    collections = []
    json_includes_id = False

    def to_dict(self):
        result = {}
        for column in self.__class__.__mapper__.columns:
            if column.name in ('producer_id', 'location_id', 'event_id'):
                continue
            if column.name == 'id' and not self.json_includes_id:
                continue
            result[column.name] = {'value': getattr(self, column.name)}
        for name in self.collections:
            if hasattr(self, name):
                result[name] = {'value': []}
                collection = getattr(self, name)
                for obj in collection:
                    result[name]['value'].append(obj.to_dict())
        return result

    @classmethod
    def appstruct_list_to_objects(cls, appstruct_list):
        objects = []
        for appstruct in appstruct_list:
            obj = cls()
            obj.update_from_appstruct(appstruct)
            objects.append(obj)
        return objects

    def update_from_appstruct(self, appstruct):
        appstruct = flatten_values(appstruct)
        for key, value in appstruct.items():
            if isinstance(value, list):
                klass = collection_classes[key]
                value = klass.appstruct_list_to_objects(appstruct.get(key, []))
            setattr(self, key, value)


class Sound(ModelMixin, Base):
    __tablename__ = 'sounds'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    license = Column(UnicodeText(20))
    url = default_column()


class Video(ModelMixin, Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    license = Column(UnicodeText(20))
    url = default_column()


class Image(ModelMixin, Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    license = Column(UnicodeText(20))
    url = default_column()


tag_association = Table(
    'tag_association', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('event_id', Integer, ForeignKey('events.id'))
)


category_association = Table(
    'category_association', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('event_id', Integer, ForeignKey('events.id'))
)


class Tag(ModelMixin, Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText(TAG_MAX_LENGTH))


class Event(ModelMixin, Base):
    __tablename__ = 'events'
    collections = ['locations', 'sounds', 'videos', 'images']
    json_includes_id = True
    id = Column(Integer, primary_key=True)

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
    press_url = default_column()
    price_information = default_column()
    source = default_column()
    source_id = default_column()
    target = default_column()
    telephone = default_column()
    title = default_column()
    uid = Column(Unicode(SAFE_MAX_LENGTH), unique=True)
    url = default_column()
    producer_id = default_column()

    locations = relationship('Location')
    sounds = relationship('Sound')
    videos = relationship('Video')
    images = relationship('Image')
    tags = relationship('Tag', secondary=tag_association)
    categories = relationship('Tag', secondary=category_association)

    def __init__(self, *args, **kwargs):
        if 'uid' not in kwargs:
            kwargs['uid'] = self.make_uid()
        self.update_from_appstruct(kwargs)

    def make_uid(self):
        return "{}@{}".format(
            uuid1().hex,
            pyramid.threadlocal.get_current_registry().settings['domain'],
        )


class Location(ModelMixin, Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    collections = ['dates']

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
    json_includes_id = True
    id = Column(Integer, primary_key=True)
    url = default_column()
    producer_id = default_column()

    def __init__(self, *args, **kwargs):
        kwargs = flatten_values(kwargs)
        super(Source, self).__init__(*args, **kwargs)


icalendar_to_model_keys = {
    'uid': 'uid',
    'summary': 'title',
    'url': 'url',
    'description': 'description',
}


def flatten_values(mapping):
    result = {}
    for key, field in mapping.items():
        if isinstance(field, dict):
            result[key] = field['value']
        else:
            result[key] = field
    return result

collection_classes = {
    'dates': Date,
    'locations': Location,
    'sounds': Sound,
    'videos': Video,
    'images': Image,
    'tags': Tag,
    'categories': Tag,
}
