from django.contrib import admin
from .models import User, CollegeIDAllowlist

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'college_id', 'role', 'email', 'is_verified')
    list_filter = ('role', 'is_verified')
    search_fields = ('username', 'full_name', 'college_id', 'email')

@admin.register(CollegeIDAllowlist)
class CollegeIDAllowlistAdmin(admin.ModelAdmin):
    list_display = ('college_id', 'email', 'role', 'is_used')
    list_filter = ('role', 'is_used')
    search_fields = ('college_id', 'email')