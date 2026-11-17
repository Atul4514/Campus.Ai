from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .models import Notification


@login_required
def notification_list(request):
    """Returns the 20 most recent notifications + unread count (JSON)."""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:20]

    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'notif_type': n.notif_type,
        'is_read': n.is_read,
        'link': n.link,
        'created_at': n.created_at.strftime('%d %b, %I:%M %p'),
    } for n in notifications]

    unread_count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    return JsonResponse({'notifications': data, 'unread_count': unread_count})


@login_required
def unread_count(request):
    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    return JsonResponse({'count': count})


@login_required
@require_POST
def mark_read(request, notif_id):
    Notification.objects.filter(
        id=notif_id, recipient=request.user
    ).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
def notification_page(request):
    """HTML page that lists recent notifications and marks them all read."""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:50]
    # Mark all as read on page visit
    Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)
    return render(request, 'core/notifications.html', {
        'notifications': notifications,
    })

