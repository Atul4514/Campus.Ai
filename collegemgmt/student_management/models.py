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

    BLOOD_GROUP_CHOICES = [
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    SEMESTER_CHOICES = [
        ('', 'Select Semester'),
        ('1', 'Semester 1'), ('2', 'Semester 2'),
        ('3', 'Semester 3'), ('4', 'Semester 4'),
        ('5', 'Semester 5'), ('6', 'Semester 6'),
        ('7', 'Semester 7'), ('8', 'Semester 8'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
    )
    profile_photo = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    roll_number = models.CharField(max_length=30, blank=True, default='')
    year = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True, default='')
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, blank=True, default='')
    section = models.CharField(max_length=20, blank=True, default='')
    course = models.CharField(max_length=100, blank=True, default='', help_text='e.g. B.Tech, MBA, BCA')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, default='')
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

    @property
    def profile_completion(self):
        """Return a percentage (0–100) of how many key fields are filled."""
        fields = [
            getattr(self.user, 'full_name', ''),
            self.roll_number,
            self.year,
            self.semester,
            self.section,
            self.course,
            self.phone_number,
            self.blood_group,
            self.address,
            self.date_of_birth,
            self.guardian_name,
            self.guardian_phone,
            bool(self.profile_photo),
        ]
        filled = sum(1 for f in fields if f)
        return round((filled / len(fields)) * 100)
