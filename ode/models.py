import pyramid
from sqlalchemy import (Column, Index, Integer, Text, Unicode, UnicodeText,
                        DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


SAFE_MAX_LENGTH = 1000


def default_column():
    return Column(Unicode(SAFE_MAX_LENGTH))


class Event(Base):
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
    url = default_column()
    video_license = default_column()
    video_url = default_column()

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in Event.__mapper__.columns
        }

    @property
    def uid(self):
        return "{}-{}@{}".format(
            self.start_time.strftime("%Y%m%d%H%M%S"),
            self.id,
            pyramid.threadlocal.get_current_registry().settings['domain'],
        )


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    start = Column(DateTime)
    end = Column(DateTime)

Index('event_index', MyModel.name, unique=True, mysql_length=255)
