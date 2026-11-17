from django.conf import settings
from django.db import models
from academics.models import Subject


class AttendanceSession(models.Model):
    """
    Represents one attendance-marking event for a particular class slot.
    Faculty create one session per lecture/lab they want to mark.
    """
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='attendance_sessions')
    section = models.CharField(max_length=20, blank=True)
    date = models.DateField()
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_sessions',
        limit_choices_to={'role__in': ['faculty', 'admin']},
    )
    topic = models.CharField(max_length=200, blank=True, help_text='Lecture topic (optional)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Attendance Session'
        verbose_name_plural = 'Attendance Sessions'

    def __str__(self):
        return f'{self.subject} — {self.date} (Sem {self.subject.semester})'

    @property
    def department(self):
        return self.subject.department

    @property
    def semester(self):
        return self.subject.semester

    @property
    def total_students(self):
        return self.records.count()

    @property
    def present_count(self):
        return self.records.filter(status__in=['P', 'L']).count()

    @property
    def attendance_percentage(self):
        total = self.total_students
        if total == 0:
            return 0
        return round((self.present_count / total) * 100, 1)


class AttendanceRecord(models.Model):
    """
    One attendance entry per student per session.
    """
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('E', 'Excused'),
    ]

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'student'},
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    marked_at = models.DateTimeField(auto_now=True)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('session', 'student')
        ordering = ['student__full_name']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f'{self.student.full_name} — {self.session} — {self.get_status_display()}'

    @property
    def is_present(self):
        return self.status in ('P', 'L')
