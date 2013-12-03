import json

from icalendar import Calendar
from ode.models import icalendar_to_model_keys


def icalendar_to_cstruct(icalendar_event):
    result = {}
    for icalendar_key, model_attribute in icalendar_to_model_keys.items():
        if icalendar_key in icalendar_event:
            result[model_attribute] = {'value': icalendar_event[icalendar_key]}
    if 'location' in icalendar_event:
        location = {'name': {'value': icalendar_event['location']}}
        result['locations'] = {'value': [location]}
        if 'dtstart' in icalendar_event and 'dtend' in icalendar_event:
            date = {
                'start_time': {
                    'value': icalendar_event['dtstart'].dt.isoformat()
                },
                'end_time': {'value': icalendar_event['dtend'].dt.isoformat()},
            }
            location['dates'] = {'value': [date]}
    return result


def icalendar_extractor(request):
    calendar = Calendar.from_ical(request.body)
    events = []
    for icalendar_event in calendar.walk()[1:]:
        cstruct = icalendar_to_cstruct(icalendar_event)
        events.append({'data': cstruct})
    return {'collection': {'items': events}}


def data_list_to_dict(data_list):
    result = {}
    for data_field in data_list:
        key = data_field['name']
        new_value = data_field['value']
        if key in result:
            existing_value = result[key]['value']
            if isinstance(existing_value, list):
                existing_value.append(new_value)
            else:
                result[key]['value'] = [existing_value, new_value]
        else:
            result[key] = {'value': new_value}
    return result


def collection_json_to_cstruct(collection_object):
    items = collection_object['collection']['items']
    for item in items:
        item['data'] = data_list_to_dict(item['data'])
    return collection_object


def json_extractor(request):
    if request.body:
        json_data = json.loads(request.body)
        if 'collection' in json_data:
            return collection_json_to_cstruct(json_data)
        else:
            return json_data
    else:
        return {}
