import datetime
import csv
import six
from StringIO import StringIO

from icalendar import Calendar, Event
from pyramid.renderers import JSON


from ode.models import icalendar_to_model_keys
from ode.deserializers import data_list_to_dict
from ode.models import Event as EventModel, Location


class IcalRenderer(object):

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            response.content_type = 'text/calendar'
        calendar = Calendar()
        for item in value['collection']['items']:
            self.add_event(calendar, data_list_to_dict(item['data']))
        return calendar.to_ical()

    @staticmethod
    def add_event(calendar, event_data):
        event = Event()
        for icalendar_key, model_attribute in icalendar_to_model_keys.items():
            if model_attribute in event_data:
                if event_data[model_attribute] is not None:
                    event.add(icalendar_key, event_data[model_attribute])
        calendar.add_component(event)


class NoContentRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            response.content_type = None
            response.status_code = 204
        return None


class CsvRenderer(object):

    MEDIA_ATTRIBUTES = ['images', 'sounds', 'videos']

    def __init__(self, info):
        pass

    @classmethod
    def format_media(cls, items):
        parts = [
            u'{} ({})'.format(item['url'], item['license'])
            for item in items
        ]
        return cls.format_list(parts)

    @staticmethod
    def format_list(parts):
        return u', '.join(parts).encode('utf-8')

    @classmethod
    def format_value(cls, key, value):
        if isinstance(value, six.string_types):
            return value.encode('utf-8')
        elif isinstance(value, list):
            if key in cls.MEDIA_ATTRIBUTES:
                return cls.format_media(value)
            else:
                return cls.format_list(value)
        elif isinstance(value, datetime.datetime):
            return value.isoformat()
        else:
            return value

    @classmethod
    def build_csv(cls, items):
        fieldnames = [column.name for column in EventModel.__mapper__.columns]
        fieldnames += ['location_' + column.name
                       for column in Location.__mapper__.columns
                       if column.name != 'event_id']
        fieldnames += ['tags', 'categories'] + cls.MEDIA_ATTRIBUTES
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            data_dict = data_list_to_dict(item['data'])
            for key, value in data_dict.items():
                data_dict[key] = cls.format_value(key, value)
            writer.writerow(data_dict)
        return output.getvalue()

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            response.content_type = 'text/csv'
        items = value['collection']['items']
        if items:
            return self.build_csv(items)
        else:
            return u''


def datetime_adapter(obj, request):
    return obj.isoformat()


JsonRenderer = JSON()
JsonRenderer.add_adapter(datetime.datetime, datetime_adapter)
