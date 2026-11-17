from django.db import models
from django.conf import settings
from academics.models import Subject


class FacultyProfile(models.Model):
    DESIGNATION_CHOICES = [
        ('assistant_professor', 'Assistant Professor'),
        ('associate_professor', 'Associate Professor'),
        ('professor', 'Professor'),
        ('lecturer', 'Lecturer'),
        ('hod', 'Head of Department'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_profile',
        limit_choices_to={'role': 'faculty'}
    )
    employee_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    designation = models.CharField(max_length=30, choices=DESIGNATION_CHOICES, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    joined_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.designation or 'No designation'}"


class SubjectAssignment(models.Model):
    """
    Which subjects a faculty member teaches, and to which department/semester.
    This becomes important later — Module 5 will check this before letting
    a faculty member mark attendance for a subject.
    """
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='faculty_assignments')
    section = models.CharField(max_length=10, blank=True)

    class Meta:
        unique_together = ('faculty', 'subject', 'section')

    def __str__(self):
        return f"{self.faculty.user.username} - {self.subject} (Sem {self.subject.semester})"
