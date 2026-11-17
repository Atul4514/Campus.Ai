"""
Notification helpers — import and call these from any app's signals.py.
All functions use bulk_create so they emit a single INSERT per event, not one per user.
"""
from django.contrib.auth import get_user_model


def send_notification(recipient, title, message, notif_type='system', link=''):
    """Create a single notification for one user."""
    from .models import Notification
    Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notif_type=notif_type,
        link=link,
    )


def send_bulk_notification(recipients, title, message, notif_type='system', link=''):
    """
    Create notifications for a queryset or list of User objects.
    Uses bulk_create — one DB INSERT regardless of recipient count.
    """
    from .models import Notification
    User = get_user_model()

    # Accept either a queryset or a plain list
    if hasattr(recipients, 'iterator'):
        recipient_list = list(recipients.values_list('pk', flat=True))
    else:
        recipient_list = [r.pk if hasattr(r, 'pk') else r for r in recipients]

    Notification.objects.bulk_create([
        Notification(
            recipient_id=pk,
            title=title,
            message=message,
            notif_type=notif_type,
            link=link,
        )
        for pk in recipient_list
    ], ignore_conflicts=True)
