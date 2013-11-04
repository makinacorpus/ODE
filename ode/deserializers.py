from icalendar import Calendar
from ode.models import icalendar_to_model_keys


def icalendar_to_cstruct(icalendar_event):
    result = {}
    for icalendar_key, model_attribute in icalendar_to_model_keys.items():
        if icalendar_key in icalendar_event:
            result[model_attribute] = icalendar_event[icalendar_key]
    for time_key in ('start_time', 'end_time'):
        if time_key in result:
            result[time_key] = result[time_key].dt.isoformat()
    return result


def icalendar_extractor(request):
    calendar = Calendar.from_ical(request.body)
    events = []
    for icalendar_event in calendar.walk()[1:]:
        cstruct = icalendar_to_cstruct(icalendar_event)
        events.append(cstruct)
    return {'events': events}
