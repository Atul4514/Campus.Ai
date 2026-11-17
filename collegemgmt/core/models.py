from django.db import models
from django.conf import settings


class AccessLog(models.Model):
    ACTION_CHOICES = [
        ('view', 'Viewed'),
        ('update', 'Updated'),
    ]

    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='access_logs_made'
    )
    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='access_logs_received'
    )
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, default='view')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.viewer} {self.action} {self.model_name}#{self.object_id} (subject: {self.subject})"


class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('notice', 'Notice Posted'),
        ('note_upload', 'Note Uploaded'),
        ('timetable_change', 'Timetable Change'),
        ('complaint_update', 'Complaint Update'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"[{self.notif_type}] {self.title} → {self.recipient}"