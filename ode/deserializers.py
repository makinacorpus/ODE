from icalendar import Calendar
from ode.models import icalendar_to_model_keys


def icalendar_to_cstruct(icalendar_event):
    result = {}
    for icalendar_key, model_attribute in icalendar_to_model_keys.items():
        if icalendar_key in icalendar_event:
            result[model_attribute] = icalendar_event[icalendar_key]
    if 'location' in icalendar_event:
        location = {'name': icalendar_event['location']}
        result['locations'] = [location]
        if 'dtstart' in icalendar_event and 'dtend' in icalendar_event:
            date = {
                'start_time': icalendar_event['dtstart'].dt.isoformat(),
                'end_time': icalendar_event['dtend'].dt.isoformat(),
            }
            location['dates'] = [date]
    return result


def icalendar_extractor(request):
    calendar = Calendar.from_ical(request.body)
    events = []
    for icalendar_event in calendar.walk()[1:]:
        cstruct = icalendar_to_cstruct(icalendar_event)
        events.append({'data': cstruct})
    return {'collection': {'items': events}}
