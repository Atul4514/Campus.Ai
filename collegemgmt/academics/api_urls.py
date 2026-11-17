from django.urls import path
from django.http import JsonResponse
from .models import TimetableEntry


def timetable_json(request):
    entries = TimetableEntry.objects.select_related('subject', 'faculty').all()
    return JsonResponse({'results': [
        {
            'id': entry.pk,
            'subject': entry.subject.name,
            'department': entry.subject.department,
            'semester': entry.subject.semester,
            'section': entry.section,
            'faculty': entry.faculty_id,
            'day_of_week': entry.day_of_week,
            'start_time': entry.start_time.isoformat(),
            'end_time': entry.end_time.isoformat(),
            'room': entry.room,
        }
        for entry in entries
    ]})

app_name = 'academics_api'
urlpatterns = [
    path('timetable/', timetable_json, name='timetable'),
]
