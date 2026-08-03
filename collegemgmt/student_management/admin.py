from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'roll_number', 'course', 'year', 'semester',
        'section', 'blood_group', 'phone_number', 'profile_completion_display', 'updated_at',
    )
    list_filter = ('year', 'semester', 'blood_group', 'section')
    search_fields = (
        'user__username', 'user__full_name', 'user__college_id',
        'roll_number', 'course', 'semester', 'section',
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Photo', {'fields': ('profile_photo',)}),
        ('Academic Info', {'fields': ('roll_number', 'course', 'year', 'semester', 'section')}),
        ('Personal Info', {'fields': ('phone_number', 'blood_group', 'date_of_birth', 'address')}),
        ('Guardian Info', {'fields': ('guardian_name', 'guardian_phone', 'emergency_contact')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Completion %')
    def profile_completion_display(self, obj):
        pct = obj.profile_completion
        color = '#22c55e' if pct >= 80 else '#f59e0b' if pct >= 50 else '#ef4444'
        return f'<span style="color:{color};font-weight:bold;">{pct}%</span>'

    profile_completion_display.allow_tags = True
