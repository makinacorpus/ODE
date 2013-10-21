from colander import MappingSchema, SchemaNode, String, Length, DateTime
from colander import drop
from ode.models import SAFE_MAX_LENGTH


def default_schema_node():
    return SchemaNode(String(), missing='',
                      validator=Length(1, SAFE_MAX_LENGTH))


class EventSchema(MappingSchema):
    title = SchemaNode(String(), validator=Length(1, SAFE_MAX_LENGTH))
    audio_license = default_schema_node()
    address = default_schema_node()
    audio_license = default_schema_node()
    audio_url = default_schema_node()
    author_email = default_schema_node()
    author_firstname = default_schema_node()
    author_lastname = default_schema_node()
    author_telephone = default_schema_node()
    country = default_schema_node()
    post_code = default_schema_node()
    description = default_schema_node()
    event_id = default_schema_node()
    email = default_schema_node()
    firstname = default_schema_node()
    language = default_schema_node()
    lastname = default_schema_node()
    latlong = default_schema_node()
    location_name = default_schema_node()
    price_information = default_schema_node()
    organiser = default_schema_node()
    capacity = default_schema_node()
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
    town = default_schema_node()
    video_license = default_schema_node()
    video_url = default_schema_node()
    url = default_schema_node()
    start_time = SchemaNode(DateTime(), missing=drop)
    end_time = SchemaNode(DateTime(), missing=drop)
