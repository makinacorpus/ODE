from icalendar import Calendar


def icalendar_extractor(request):
    calendar = Calendar.from_ical(request.body)
    event = calendar.walk()[1]
    return {
        'title': event['summary'],
        'start_time': event['dtstart'].dt.isoformat(),
    }
