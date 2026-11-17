from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    readonly_fields = ('marked_at',)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'subject_department', 'subject_semester', 'section', 'date', 'faculty', 'total_students', 'attendance_percentage')
    list_filter = ('subject__department', 'subject__semester', 'date')
    search_fields = ('subject__name', 'subject__department', 'faculty__full_name')
    inlines = [AttendanceRecordInline]
    date_hierarchy = 'date'

    @admin.display(description='Department', ordering='subject__department')
    def subject_department(self, obj):
        return obj.subject.department

    @admin.display(description='Semester', ordering='subject__semester')
    def subject_semester(self, obj):
        return obj.subject.semester


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'marked_at')
    list_filter = ('status', 'session__subject__name', 'session__subject__department')
    search_fields = ('student__full_name', 'student__college_id', 'session__subject__name')
