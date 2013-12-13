import datetime
import csv
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

    def __init__(self, info):
        pass

    @staticmethod
    def build_csv(items):
        fieldnames = [column.name for column in EventModel.__mapper__.columns]
        fieldnames += ['location_' + column.name
                       for column in Location.__mapper__.columns
                       if column.name != 'event_id']
        fieldnames += ['tags', 'categories', 'videos', 'images', 'sounds']
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            data_dict = data_list_to_dict(item['data'])
            for key, value in data_dict.items():
                if value is not None:
                    if isinstance(value, basestring):
                        data_dict[key] = value.encode('utf-8')
                    elif isinstance(value, list):
                        if key in ('images', 'sounds', 'videos'):
                            medias = ['%s (%s)' % (v['url'], v['license'])
                                      for v in value]
                            data_dict[key] = u', '.join(medias).encode('utf-8')
                        else:
                            data_dict[key] = u', '.join(value).encode('utf-8')
                    elif isinstance(value, datetime.datetime):
                        data_dict[key] = value.isoformat()
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
