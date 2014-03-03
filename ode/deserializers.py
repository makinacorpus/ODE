import csv
import json
import re
import six
from six import StringIO

from ics import Calendar
from ics.parse import ParseError


def default_extractor(attribute):
    def extractor(event):
        if hasattr(event, attribute):
            return getattr(event, attribute)

    return extractor


def date_exractor(attribute):
    def extractor(event):
        if hasattr(event, attribute):
            return getattr(event, attribute).format('YYYY-MM-DDTHH:mm:ss')

    return extractor


def url_extractor(event):
    for line in event._unused:
        if line.name == 'URL':
            return line.value


icalendar_to_model_keys = {
    'id': default_extractor('uid'),
    'title': default_extractor('name'),
    'url': url_extractor,
    'description': default_extractor('description'),
    'end_time': date_exractor('end'),
    'start_time': date_exractor('begin'),
    'location_name': default_extractor('location'),
}


def icalendar_to_cstruct(icalendar_event):
    result = {}
    for model_attribute, extractor in icalendar_to_model_keys.items():
        value = extractor(icalendar_event)
        if value:
            result[model_attribute] = value
    return result


def icalendar_extractor(request):
    items = []
    try:
        text = request.text
        calendar = Calendar(text)
        for icalendar_event in calendar.events:
            cstruct = icalendar_to_cstruct(icalendar_event)
            items.append({'data': cstruct})
    except ParseError as exc:
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
    if request.text:
        try:
            json_data = json.loads(request.text)
        except ValueError as e:
            request.errors.add(
                'body', None,
                "Invalid JSON request body: %s" % e)
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


def csv_text(text):
    if six.PY2:
        return text.encode('utf-8')
    else:
        return text


def csv_extractor(request):
    items = []
    if request.text:
        reader = csv.DictReader(StringIO(csv_text(request.text)))
        for row in reader:
            data_dict = {
                key: value.decode('utf-8') if six.PY2 else value
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
