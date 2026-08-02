from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'semester', 'section', 'updated_at')
    search_fields = ('user__username', 'user__full_name', 'roll_number', 'semester', 'section')
