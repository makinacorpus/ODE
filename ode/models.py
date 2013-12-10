import pyramid
from sqlalchemy import (Column, Integer, Unicode, UnicodeText,
                        DateTime, ForeignKey, Boolean, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import Table
from uuid import uuid1
from zope.sqlalchemy import ZopeTransactionExtension

from ode.urls import absolute_url


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


SAFE_MAX_LENGTH = 1000
TAG_MAX_LENGTH = 50


def default_column():
    return Column(Unicode(SAFE_MAX_LENGTH))


class BaseModel(object):

    id = Column(Integer, primary_key=True)

    def to_data_list(self):
        result = []
        for column in self.__class__.__mapper__.columns:
            if column.name in ('provider_id', 'location_id', 'event_id'):
                continue
            result.append({'name': column.name,
                           'value': getattr(self, column.name)})
        return result

    @classmethod
    def list_to_objects(cls, appstruct_list):
        objects = []
        for appstruct in appstruct_list:
            if cls is Tag:
                obj = cls(name=appstruct)
            else:
                obj = cls(**appstruct)
            objects.append(obj)
        return objects

    def update_from_appstruct(self, appstruct):
        for key, value in appstruct.items():
            if isinstance(value, list):
                klass = collection_classes[key]
                value = klass.list_to_objects(appstruct.get(key, []))
            if isinstance(self, Tag):
                self.name = value
            else:
                if key.startswith('location_'):
                    if self.location is None:
                        self.location = Location()
                    key = key.replace('location_', '')
                    setattr(self.location, key, value)
                setattr(self, key, value)

    def to_item(self, request):
        return {
            "data": self.to_data_list(),
            'href': self.absolute_url(request),
        }

    def absolute_url(self, request):
        route_name = self.__class__.__name__.lower() + 'resource'
        return absolute_url(request, route_name, id=self.id)

    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter_by(id=id).first()


Base = declarative_base(cls=BaseModel)


class Media(Base):
    __tablename__ = 'media'
    event_id = Column(Integer, ForeignKey('events.id'))
    license = Column(UnicodeText(20))
    url = default_column()
    type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'media'
    }


class Sound(Media):
    __mapper_args__ = {
        'polymorphic_identity': 'sound'
    }


class Video(Media):
    __mapper_args__ = {
        'polymorphic_identity': 'video'
    }


class Image(Media):
    __mapper_args__ = {
        'polymorphic_identity': 'image'
    }


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


class Tag(Base):
    __tablename__ = 'tags'
    name = Column(UnicodeText(TAG_MAX_LENGTH), unique=True)


class Event(Base):
    __tablename__ = 'events'

    id = Column(Unicode(SAFE_MAX_LENGTH), unique=True, primary_key=True)

    firstname = default_column()
    lastname = default_column()
    email = default_column()
    telephone = default_column()
    description = Column(UnicodeText(SAFE_MAX_LENGTH))
    language = default_column()
    latlong = default_column()
    organiser = default_column()
    performers = default_column()
    press_url = default_column()
    price_information = default_column()
    source = default_column()
    source_id = default_column()
    target = default_column()
    title = default_column()
    url = default_column()
    provider_id = default_column()
    start_time = Column(DateTime(timezone=False))
    end_time = Column(DateTime(timezone=False))
    publication_start = Column(DateTime(timezone=False))
    publication_end = Column(DateTime(timezone=False))

    location = relationship('Location', uselist=False)
    sounds = relationship('Sound')
    videos = relationship('Video')
    images = relationship('Image')
    tags = relationship('Tag', secondary=tag_association)
    categories = relationship('Tag', secondary=category_association)

    press_contact_email = default_column()
    press_contact_name = default_column()
    press_contact_phone_number = default_column()
    ticket_contact_email = default_column()
    ticket_contact_name = default_column()
    ticket_contact_phone_number = default_column()

    def __init__(self, *args, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = self.make_uid()
        self.update_from_appstruct(kwargs)

    def make_uid(self):
        return "{}@{}".format(
            uuid1().hex,
            pyramid.threadlocal.get_current_registry().settings['domain'],
        )

    def to_data_list(self):
        result = []

        for column in self.__class__.__mapper__.columns:
            if column.name == 'provider_id':
                continue
            result.append({'name': column.name,
                           'value': getattr(self, column.name)})

        if getattr(self, 'location', None):
            location_fields = ('name', 'address', 'post_code', 'capacity',
                               'town', 'country')
            for name in location_fields:
                result.append({'name': 'location_' + name,
                               'value': getattr(self.location, name)})

        for attrname in ('tags', 'categories'):
            objects = getattr(self, attrname, None)
            if objects:
                values = [obj.name for obj in objects]
                result.append({'name': attrname, 'value': values})

        for attrname in ('images', 'videos', 'sounds'):
            objects = getattr(self, attrname, None)
            if objects:
                values = [{'url': obj.url, 'license': obj.license}
                          for obj in objects]
                result.append({'name': attrname, 'value': values})
        return result


class Location(Base):
    __tablename__ = 'locations'

    name = default_column()
    address = default_column()
    post_code = default_column()
    capacity = default_column()
    town = default_column()
    country = default_column()
    event_id = Column(Integer, ForeignKey('events.id'))


class Source(Base):
    __tablename__ = 'sources'
    url = default_column()
    active = Column(Boolean())
    provider_id = default_column()


icalendar_to_model_keys = {
    'uid': 'id',
    'summary': 'title',
    'url': 'url',
    'description': 'description',
    'dtend': 'end_time',
    'dtstart': 'start_time',
    'location': 'location_name',
}


collection_classes = {
    'locations': Location,
    'sounds': Sound,
    'videos': Video,
    'images': Image,
    'tags': Tag,
    'categories': Tag,
}
