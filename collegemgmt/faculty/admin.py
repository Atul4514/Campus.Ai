from django.contrib import admin
from .models import FacultyProfile, SubjectAssignment


class SubjectAssignmentInline(admin.TabularInline):
    model = SubjectAssignment
    extra = 1


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'designation', 'experience_years')
    list_filter = ('designation',)
    search_fields = ('user__username', 'employee_id')
    inlines = [SubjectAssignmentInline]


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'subject', 'subject_department', 'subject_semester', 'section')
    list_filter = ('subject__department', 'subject__semester')
    search_fields = ('subject__name', 'faculty__user__username')

    @admin.display(description='Department', ordering='subject__department')
    def subject_department(self, obj):
        return obj.subject.department

    @admin.display(description='Semester', ordering='subject__semester')
    def subject_semester(self, obj):
        return obj.subject.semester
