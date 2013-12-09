from colander import MappingSchema, SchemaNode, String, Integer, Boolean
from colander import Length, DateTime, instantiate
from colander import SequenceSchema, OneOf, drop
import colander

from models import TAG_MAX_LENGTH, SAFE_MAX_LENGTH


def has_provider_id(request):
    provider_id = request.headers.get('X-ODE-Provider-Id', '').strip()
    if provider_id:
        request.validated['provider_id'] = provider_id
    else:
        request.errors.add('body', 'provider_id',
                           'This request requires an X-ODE-Provider-Id header')
        request.errors.status = 403


def default_schema_node():
    class _DefaultFieldSchema(MappingSchema):
        value = SchemaNode(String(), missing='',
                           validator=Length(1, SAFE_MAX_LENGTH))
    return _DefaultFieldSchema(missing=None)


class MediaSchema(MappingSchema):
    license = default_schema_node()
    url = default_schema_node()


class TagSchema(MappingSchema):
    value = SchemaNode(String(), validator=Length(1, TAG_MAX_LENGTH))


class EventSchema(MappingSchema):
    @instantiate()
    class title(MappingSchema):
        value = SchemaNode(String(), validator=Length(1, SAFE_MAX_LENGTH))
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
    press_url = default_schema_node()
    source_id = default_schema_node()
    source = default_schema_node()
    target = default_schema_node()
    telephone = default_schema_node()
    url = default_schema_node()

    location_name = default_schema_node()
    location_address = default_schema_node()
    location_post_code = default_schema_node()
    location_town = default_schema_node()
    location_capacity = default_schema_node()
    location_country = default_schema_node()

    @instantiate(missing=drop)
    class id(MappingSchema):
        value = SchemaNode(String(), missing=drop,
                           validator=Length(1, SAFE_MAX_LENGTH))

    @instantiate(missing={'value': []})
    class sounds(MappingSchema):

        @instantiate()
        class value(SequenceSchema):
            sound = MediaSchema()

    @instantiate(missing={'value': []})
    class videos(MappingSchema):

        @instantiate()
        class value(SequenceSchema):
            video = MediaSchema()

    @instantiate(missing={'value': []})
    class images(MappingSchema):

        @instantiate()
        class value(SequenceSchema):
            image = MediaSchema()

    @instantiate(missing={'value': []})
    class tags(MappingSchema):

        @instantiate()
        class value(SequenceSchema):
            tag = TagSchema()

    @instantiate(missing={'value': []})
    class categories(MappingSchema):

        @instantiate()
        class value(SequenceSchema):
            tag = TagSchema()

    @instantiate()
    class start_time(MappingSchema):
        value = SchemaNode(DateTime(default_tzinfo=None))

    @instantiate()
    class end_time(MappingSchema):
        value = SchemaNode(DateTime(default_tzinfo=None), missing=None)


class EventCollectionSchema(MappingSchema):

    @instantiate()
    class items(SequenceSchema):

        @instantiate()
        class item(MappingSchema):
            data = EventSchema()


class SourceSchema(MappingSchema):
    @instantiate()
    class url(MappingSchema):
        value = SchemaNode(String(), validator=colander.url)

    @instantiate(missing=False)
    class active(MappingSchema):
        value = SchemaNode(Boolean())


class SourceCollectionSchema(MappingSchema):

    @instantiate()
    class items(SequenceSchema):

        @instantiate()
        class item(MappingSchema):
            data = SourceSchema()


class QueryStringSchema(MappingSchema):
    limit = SchemaNode(Integer(), missing=None)
    offset = SchemaNode(Integer(), missing=None)
    sort_by = SchemaNode(String(), missing=None)
    sort_direction = SchemaNode(String(), missing='asc',
                                validator=OneOf(['asc', 'desc']))
    provider_id = SchemaNode(Integer(), missing=drop)


def validate_querystring(request):
    schema = QueryStringSchema()
    try:
        request.validated.update(schema.deserialize(request.GET))
    except colander.Invalid, e:
        errors = e.asdict()
        for field, message in errors.items():
            request.errors.add('body', field, message)
        request.errors.status = 400
