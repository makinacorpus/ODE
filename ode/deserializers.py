import csv
import json
import re
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
    items = []
    try:
        calendar = Calendar.from_ical(request.body)
        for icalendar_event in calendar.walk()[1:]:
            cstruct = icalendar_to_cstruct(icalendar_event)
            items.append({'data': cstruct})
    except ValueError as exc:
        request.errors.add('body', None,
                           "Invalid iCalendar request body: %s " % exc)
    cstruct = {'items': items}
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
    items = []
    if request.body:
        try:
            json_data = json.loads(request.body)
        except ValueError as e:
            request.errors.add(
                'body', None,
                "Invalid JSON request body: %s" % (e.message))
        else:
            if 'template' in json_data:
                # POST or PUT requests
                data_dict = data_list_to_dict(json_data['template']['data'])
                items = [{'data': data_dict}]
            elif 'collection' in json_data.keys():
                # harvesting
                items = []
                for item in json_data['collection']['items']:
                    data_dict = data_list_to_dict(item['data'])
                    items.append({'data': data_dict})
            else:
                request.errors.add('body', None,
                                   "Invalid Collection+JSON input")
    else:
        request.errors.add('body', None, "Empty JSON request body")
    return {'items': items}


def csv_format_data_dict(data_dict):
    media_type_csv = ['sounds', 'images', 'videos']
    list_type_csv = ['tags', 'categories']
    separator = ', '

    for list_type in list_type_csv:
        if list_type in data_dict.keys():
            data_dict[list_type] = data_dict[list_type].split(separator)
    for media_type in media_type_csv:
        if media_type in data_dict.keys():
            medias = data_dict[media_type].split(separator)
            formatted_medias = []
            for media in medias:
                m = re.match('(.+) \((.+)\)', media)
                if m:
                    formatted_medias.append({
                        'url': m.group(1),
                        'license': m.group(2)
                        })
            data_dict[media_type] = formatted_medias
    return data_dict


def csv_extractor(request):
    items = []
    if request.body:
        reader = csv.DictReader(StringIO(request.body))
        for row in reader:
            data_dict = {
                key: value.decode('utf-8')
                for key, value in row.items()
            }
            data_dict = csv_format_data_dict(data_dict)
            items.append({'data': data_dict})
        if not items:
            request.errors.add('body', None, "Invalid CSV request body")
    else:
        request.errors.add('body', None, "Empty CSV request body")
    cstruct = {'items': items}
    return cstruct
