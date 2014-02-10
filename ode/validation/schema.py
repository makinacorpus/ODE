from colander import MappingSchema, SchemaNode, String, Integer, Boolean
from colander import Length, DateTime, instantiate
from colander import SequenceSchema, OneOf, drop
import colander

from ode.models import TAG_MAX_LENGTH, SAFE_MAX_LENGTH


def default_schema_node():
    return SchemaNode(String(), missing='',
                      validator=Length(1, SAFE_MAX_LENGTH))


class MediaSchema(MappingSchema):
    license = default_schema_node()
    url = SchemaNode(String(), validator=colander.url)


def remove_timezone(dt):
    if dt is colander.null:
        return dt
    else:
        return dt.replace(tzinfo=None)


class EventSchema(MappingSchema):
    id = SchemaNode(String(), missing=drop,
                    validator=Length(1, SAFE_MAX_LENGTH))
    provider_id = default_schema_node()
    title = SchemaNode(String(), validator=Length(1, SAFE_MAX_LENGTH))
    email = SchemaNode(String(), validator=colander.Email())
    firstname = default_schema_node()
    lastname = default_schema_node()
    telephone = default_schema_node()
    description = default_schema_node()
    event_id = default_schema_node()
    email = SchemaNode(String(), missing='', validator=colander.Email())
    firstname = default_schema_node()
    language = default_schema_node()
    lastname = default_schema_node()
    latlong = default_schema_node()
    price_information = default_schema_node()
    organiser = default_schema_node()
    performers = default_schema_node()
    press_url = SchemaNode(String(), missing='', validator=colander.url)
    source_id = default_schema_node()
    source = default_schema_node()
    target = default_schema_node()
    telephone = default_schema_node()
    url = SchemaNode(String(), missing='', validator=colander.url)

    location_name = default_schema_node()
    location_address = default_schema_node()
    location_post_code = default_schema_node()
    location_town = default_schema_node()
    location_capacity = default_schema_node()
    location_country = default_schema_node()

    start_time = SchemaNode(DateTime(default_tzinfo=None),
                            preparer=remove_timezone)
    end_time = SchemaNode(DateTime(default_tzinfo=None), missing=None,
                          preparer=remove_timezone)
    publication_start = SchemaNode(DateTime(default_tzinfo=None), missing=None,
                                   preparer=remove_timezone)
    publication_end = SchemaNode(DateTime(default_tzinfo=None), missing=None,
                                 preparer=remove_timezone)

    press_contact_email = SchemaNode(String(), missing='',
                                     validator=colander.Email())
    press_contact_name = default_schema_node()
    press_contact_phone_number = default_schema_node()
    ticket_contact_email = SchemaNode(String(), missing='',
                                      validator=colander.Email())
    ticket_contact_name = default_schema_node()
    ticket_contact_phone_number = default_schema_node()

    @instantiate(missing=[])
    class videos(SequenceSchema):
        video = MediaSchema()

    @instantiate(missing=[])
    class sounds(SequenceSchema):
        sound = MediaSchema()

    @instantiate(missing=[])
    class images(SequenceSchema):
        image = MediaSchema()

    @instantiate(missing=[])
    class tags(SequenceSchema):
        name = SchemaNode(String(), validator=Length(1, TAG_MAX_LENGTH))

    @instantiate(missing=[])
    class categories(SequenceSchema):
        name = SchemaNode(String(), validator=Length(1, TAG_MAX_LENGTH))


class EventCollectionSchema(MappingSchema):

    @instantiate()
    class items(SequenceSchema):

        @instantiate()
        class item(MappingSchema):
            data = EventSchema()


class SourceSchema(MappingSchema):
    url = SchemaNode(String(), validator=colander.url)
    active = SchemaNode(Boolean(), missing=False)


class SourceCollectionSchema(MappingSchema):

    @instantiate()
    class items(SequenceSchema):

        @instantiate()
        class item(MappingSchema):
            data = SourceSchema()


COLLECTION_MAX_LENGTH = 50


class QueryStringSchema(MappingSchema):
    limit = SchemaNode(Integer(), missing=drop,
                       validator=colander.Range(0, COLLECTION_MAX_LENGTH))
    offset = SchemaNode(Integer(), missing=drop)
    sort_by = SchemaNode(String(), missing=drop)
    sort_direction = SchemaNode(String(), missing='asc',
                                validator=OneOf(['asc', 'desc']))
    provider_id = SchemaNode(String(), missing=drop,
                             validator=Length(1, SAFE_MAX_LENGTH))
    start_time = SchemaNode(DateTime(default_tzinfo=None), missing=drop)
    end_time = SchemaNode(DateTime(default_tzinfo=None), missing=drop)
