from icalendar import Calendar


def icalendar_to_event_dict(event):
    return {
        'uid': event['uid'],
        'title': event['summary'],
        'start_time': event['dtstart'].dt,
        'end_time': event['dtend'].dt,
        'title': event['summary'],
        'url': event.get('url'),
        'description': event.get('description'),
        'location_name': event.get('location'),
    }


def icalendar_extractor(request):
    calendar = Calendar.from_ical(request.body)
    events = []
    for event in calendar.walk()[1:]:
        event_dict = icalendar_to_event_dict(event)
        event_dict['start_time'] = event_dict['start_time'].isoformat()
        event_dict['end_time'] = event_dict['end_time'].isoformat()
        events.append(event_dict)
    return {'events': events}
