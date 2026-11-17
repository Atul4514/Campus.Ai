from django.urls import path, include
from .views import (
    FacultyProfileViewSet,
    manage_faculty_page, edit_faculty_page, delete_faculty_page,
    my_faculty_profile_page, my_students_page,
)

app_name = 'faculty'

urlpatterns = [
    path('manage/', manage_faculty_page, name='manage_faculty_page'),
    path('manage/<int:faculty_id>/edit/', edit_faculty_page, name='edit_faculty'),
    path('manage/<int:faculty_id>/delete/', delete_faculty_page, name='delete_faculty'),
    path('my-profile/', my_faculty_profile_page, name='my_faculty_profile_page'),
    path('my-students/', my_students_page, name='my_students'),
]
