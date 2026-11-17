from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    ]

    full_name = models.CharField(max_length=150)
    college_id = models.CharField(max_length=20, unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', db_index=True)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.username} ({self.college_id})"


class CollegeIDAllowlist(models.Model):
    college_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    role = models.CharField(max_length=10, choices=User.ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "College ID Allowlist"

    def __str__(self):
        return f"{self.college_id} - {self.email}"


# ---------- Signals: auto-create role-specific profiles on registration ----------

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            from student_management.models import StudentProfile
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == 'faculty':
            from faculty.models import FacultyProfile
            FacultyProfile.objects.get_or_create(user=instance)
