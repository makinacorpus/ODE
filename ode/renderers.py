import datetime

from icalendar import Calendar, Event
from pyramid.renderers import JSON


from ode.models import icalendar_to_model_keys


class IcalRenderer(object):

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            response.content_type = 'text/calendar'
        calendar = Calendar()
        if 'collection' in value:
            for item in value['collection']['items']:
                self.add_event(calendar, item['data'])
        else:
            event_data = value['event']
            self.add_event(calendar, event_data)
        return calendar.to_ical()

    @staticmethod
    def add_event(calendar, event_data):
        event = Event()
        for icalendar_key, model_attribute in icalendar_to_model_keys.items():
            event.add(icalendar_key, event_data[model_attribute])
        location = event_data['locations'][0]
        event.add('location', location['name'])
        date = location['dates'][0]
        event.add('dtstart', date['start_time'])
        event.add('dtend', date['end_time'])
        calendar.add_component(event)


def datetime_adapter(obj, request):
    return obj.isoformat()


JsonRenderer = JSON()
JsonRenderer.add_adapter(datetime.datetime, datetime_adapter)
