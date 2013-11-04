import pyramid
from sqlalchemy import (Column, Integer, Unicode, UnicodeText,
                        DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from uuid import uuid1
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


SAFE_MAX_LENGTH = 1000


def default_column():
    return Column(Unicode(SAFE_MAX_LENGTH))


class ModelMixin(object):

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__class__.__mapper__.columns
            if column.name != 'owner_id'
        }


class Event(ModelMixin, Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)

    address = default_column()
    audio_license = default_column()
    audio_url = default_column()
    author_email = default_column()
    author_firstname = default_column()
    author_lastname = default_column()
    author_telephone = default_column()
    capacity = default_column()
    country = default_column()
    description = Column(UnicodeText(SAFE_MAX_LENGTH))
    email = default_column()
    end_time = Column(DateTime)
    event_id = default_column()
    firstname = default_column()
    language = default_column()
    lastname = default_column()
    latlong = default_column()
    location_name = default_column()
    organiser = default_column()
    performers = default_column()
    photos1_license = default_column()
    photos1_url = default_column()
    photos2_license = default_column()
    photos2_url = default_column()
    post_code = default_column()
    press_url = default_column()
    price_information = default_column()
    source = default_column()
    source_id = default_column()
    start_time = Column(DateTime)
    target = default_column()
    telephone = default_column()
    title = default_column()
    town = default_column()
    uid = Column(Unicode(SAFE_MAX_LENGTH), unique=True)
    url = default_column()
    video_license = default_column()
    video_url = default_column()
    owner_id = default_column()

    def __init__(self, *args, **kwargs):
        if 'uid' not in kwargs and 'start_time' in kwargs:
            kwargs['uid'] = self.make_uid(kwargs['start_time'])
        super(Event, self).__init__(*args, **kwargs)

    def make_uid(self, start_time):
        return "{}-{}@{}".format(
            start_time.strftime("%Y%m%d%H%M%S"),
            uuid1().hex,
            pyramid.threadlocal.get_current_registry().settings['domain'],
        )


class Source(ModelMixin, Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    url = default_column()
    owner_id = default_column()
