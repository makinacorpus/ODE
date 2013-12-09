import json
import csv
from StringIO import StringIO

from icalendar import Calendar
from ode.models import icalendar_to_model_keys


def icalendar_to_cstruct(icalendar_event):
    result = {}
    for icalendar_key, model_attribute in icalendar_to_model_keys.items():
        if icalendar_key in icalendar_event:
            if icalendar_key in ('dtstart', 'dtend'):
                result[model_attribute] = \
                    icalendar_event[icalendar_key].dt.isoformat()
            else:
                result[model_attribute] = icalendar_event[icalendar_key]
    return result


def icalendar_extractor(request):
    calendar = Calendar.from_ical(request.body)
    events = []
    for icalendar_event in calendar.walk()[1:]:
        cstruct = icalendar_to_cstruct(icalendar_event)
        events.append({'data': cstruct})
    cstruct = {'items': events}
    return cstruct


def data_list_to_dict(data_list):
    result = {}
    for data_field in data_list:
        key = data_field['name']
        new_value = data_field['value']
        if key in result:
            existing_value = result[key]
            if isinstance(existing_value, list):
                existing_value.append(new_value)
            else:
                result[key] = [existing_value, new_value]
        else:
            result[key] = new_value
    return result


def json_extractor(request):
    if request.body:
        json_data = json.loads(request.body)
        if 'template' in json_data:
            data_dict = data_list_to_dict(json_data['template']['data'])
            cstruct = {
                'items': [{'data': data_dict}]
            }
            return cstruct
        else:
            return json_data
    else:
        return {}


def csv_extractor(request):
    if request.body:
        reader = csv.DictReader(StringIO(request.body))
        items = []
        for row in reader:
            data_dict = {
                key: value.decode('utf-8')
                for key, value in row.items()
            }
            items.append({'data': data_dict})
        cstruct = {'items': items}
        return cstruct
    else:
        return {}
