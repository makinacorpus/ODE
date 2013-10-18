from icalendar import Calendar, Event


class Ical(object):

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        event_data = value['event']
        if request is not None:
            response = request.response
            response.content_type = 'text/calendar'
        calendar = Calendar()
        event = Event()
        event.add('summary', event_data['title'])
        event.add('description', event_data['description'].strip())
        event.add('location', event_data['location_name'].strip())
        event.add('url', event_data['url'].strip())
        calendar.add_component(event)
        return calendar.to_ical()
