from colander import MappingSchema, SchemaNode, String, Integer
from colander import Length, DateTime
from colander import SequenceSchema, OneOf
import colander

from ode.models import SAFE_MAX_LENGTH


def has_producer_id(request):
    producer_id = request.headers.get('X-ODE-Producer-Id', '').strip()
    if producer_id:
        request.validated['producer_id'] = producer_id
    else:
        request.errors.add('body', 'producer_id',
                           'This request requires an X-ODE-Producer-Id header')
        request.errors.status = 403


def default_schema_node():
    return SchemaNode(String(), missing='',
                      validator=Length(1, SAFE_MAX_LENGTH))


class DateSchema(MappingSchema):
    start_time = SchemaNode(DateTime())
    end_time = SchemaNode(DateTime(), missing=None)


class DateSequenceSchema(SequenceSchema):
    date = DateSchema()


class LocationSchema(MappingSchema):
    name = default_schema_node()
    address = default_schema_node()
    post_code = default_schema_node()
    town = default_schema_node()
    capacity = default_schema_node()
    country = default_schema_node()
    dates = DateSequenceSchema()


class LocationCollectionSchema(SequenceSchema):
    location = LocationSchema()


class EventSchema(MappingSchema):
    title = SchemaNode(String(), validator=Length(1, SAFE_MAX_LENGTH))
    audio_license = default_schema_node()
    audio_license = default_schema_node()
    audio_url = default_schema_node()
    author_email = default_schema_node()
    author_firstname = default_schema_node()
    author_lastname = default_schema_node()
    author_telephone = default_schema_node()
    description = default_schema_node()
    event_id = default_schema_node()
    email = default_schema_node()
    firstname = default_schema_node()
    language = default_schema_node()
    lastname = default_schema_node()
    latlong = default_schema_node()
    price_information = default_schema_node()
    organiser = default_schema_node()
    price_information = default_schema_node()
    performers = default_schema_node()
    photos1_license = default_schema_node()
    photos1_url = default_schema_node()
    photos2_license = default_schema_node()
    photos2_url = default_schema_node()
    press_url = default_schema_node()
    source_id = default_schema_node()
    source = default_schema_node()
    target = default_schema_node()
    telephone = default_schema_node()
    title = default_schema_node()
    video_license = default_schema_node()
    video_url = default_schema_node()
    uid = SchemaNode(String(), missing=colander.drop,
                     validator=Length(1, SAFE_MAX_LENGTH))
    url = default_schema_node()
    locations = LocationCollectionSchema()


class Events(SequenceSchema):
    event = EventSchema()


class EventCollectionSchema(MappingSchema):
    events = Events()


class SourceSchema(MappingSchema):
    url = SchemaNode(String(), validator=colander.url)


class Sources(SequenceSchema):
    source = SourceSchema()


class SourceCollectionSchema(MappingSchema):
    sources = Sources()


class QueryStringSchema(MappingSchema):
    limit = SchemaNode(Integer(), missing=None)
    offset = SchemaNode(Integer(), missing=None)
    sort_by = SchemaNode(String(), missing=None)
    sort_direction = SchemaNode(String(), missing='asc',
                                validator=OneOf(['asc', 'desc']))


def validate_querystring(request):
    schema = QueryStringSchema()
    try:
        request.validated = schema.deserialize(request.GET)
    except colander.Invalid, e:
        errors = e.asdict()
        for field, message in errors.items():
            request.errors.add('body', field, message)
        request.errors.status = 400
