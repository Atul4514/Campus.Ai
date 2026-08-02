from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    YEAR_CHOICES = [
        ('', 'Select Year'),
        ('First Year', 'First Year'),
        ('Second Year', 'Second Year'),
        ('Third Year', 'Third Year'),
        ('Fourth Year', 'Fourth Year'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    profile_photo = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    roll_number = models.CharField(max_length=30, blank=True, default='')
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True, default='')
    semester = models.CharField(max_length=20, blank=True, default='')
    section = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    guardian_name = models.CharField(max_length=150, blank=True, default='')
    guardian_phone = models.CharField(max_length=15, blank=True, default='')
    emergency_contact = models.CharField(max_length=15, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"{self.user.username} profile"
