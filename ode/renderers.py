import datetime

from icalendar import Calendar, Event
from pyramid.renderers import JSON


class IcalRenderer(object):

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            response.content_type = 'text/calendar'
        calendar = Calendar()
        if 'events' in value:
            for event_data in value['events']:
                self.add_event(calendar, event_data)
        else:
            event_data = value['event']
            self.add_event(calendar, event_data)
        return calendar.to_ical()

    @staticmethod
    def add_event(calendar, event_data):
        event = Event()
        event.add('summary', event_data['title'])
        event.add('description', event_data['description'])
        event.add('location', event_data['location_name'])
        event.add('url', event_data['url'])
        event.add('dtstart', event_data['start_time'])
        event.add('dtend', event_data['end_time'])
        calendar.add_component(event)


def datetime_adapter(obj, request):
    return obj.isoformat()


JsonRenderer = JSON()
JsonRenderer.add_adapter(datetime.datetime, datetime_adapter)
