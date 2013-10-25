from icalendar import Calendar


def icalendar_extractor(request):
    calendar = Calendar.from_ical(request.body)
    event = calendar.walk()[1]
    events = []
    for event in calendar.walk()[1:]:
        events.append({
            'title': event['summary'],
            'start_time': event['dtstart'].dt.isoformat(),
        })
    return {'events': events}
