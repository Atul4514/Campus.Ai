from django.contrib import admin
from .models import Notice, StudyMaterial, TimetableEntry, Subject

admin.site.register((Notice, StudyMaterial, TimetableEntry, Subject))
