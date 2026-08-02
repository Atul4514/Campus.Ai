from django.urls import path
from .views import manage_students, my_profile, student_profile_view

app_name = 'student_management'

urlpatterns = [
    path('students/', manage_students, name='manage_students'),
    path('profile/', my_profile, name='my_profile'),
    path('profile/<int:student_id>/', student_profile_view, name='student_profile'),
]
