from django.conf import settings
from django.db import models


class AudienceModel(models.Model):
    """Reusable class audience with an optional section."""
    section = models.CharField(max_length=20, blank=True)
    section = models.CharField(max_length=20, blank=True)

    class Meta:
        abstract = True


class Subject(models.Model):
    """A canonical subject offered by a department in a semester."""
    name = models.CharField(max_length=120)
    department = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['department', 'semester', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'department', 'semester'],
                name='unique_subject_department_semester',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.department}, Sem {self.semester})'


class TimetableEntry(AudienceModel):
    DAYS = [(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])]
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='timetable_entries')
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='timetable_entries')
    day_of_week = models.PositiveSmallIntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        constraints = [models.UniqueConstraint(fields=['subject', 'section', 'day_of_week', 'start_time'], name='unique_class_slot')]

    def __str__(self):
        return f'{self.subject} — {self.get_day_of_week_display()} {self.start_time}'


class StudyMaterial(AudienceModel):
    department = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='study_materials')
    file = models.FileField(upload_to='study_materials/%Y/%m/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_materials')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Notice(AudienceModel):
    department = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=180)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, null=True, blank=True, related_name='notices')
    body = models.TextField()
    attachment = models.FileField(upload_to='notices/%Y/%m/', blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_notices')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
