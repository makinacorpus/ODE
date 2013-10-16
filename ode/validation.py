from colander import MappingSchema, SchemaNode, String, Length


class EventSchema(MappingSchema):
    title = SchemaNode(String(), validator=Length(1, 1000))
