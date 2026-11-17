from django.http import JsonResponse
from django.urls import path

from .models import AttendanceSession


def sessions_json(request):
    sessions = AttendanceSession.objects.select_related('subject', 'faculty').all()
    return JsonResponse({
        'results': [
            {
                'id': session.pk,
                'subject': session.subject.name,
                'department': session.subject.department,
                'semester': session.subject.semester,
                'section': session.section,
                'date': session.date.isoformat(),
                'faculty': session.faculty_id,
            }
            for session in sessions
        ]
    })


app_name = 'attendance_api'
urlpatterns = [path('', sessions_json, name='sessions')]
