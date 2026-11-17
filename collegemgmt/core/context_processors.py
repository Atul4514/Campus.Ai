"""
core/context_processors.py
Injects unread_notification_count into every template context
for authenticated users. Zero extra queries for anonymous users.
"""
from .models import Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {}
    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    return {'unread_notification_count': count}
