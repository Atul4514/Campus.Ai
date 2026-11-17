from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Faculty / Admin
    path('', views.session_list, name='session_list'),
    path('new/', views.session_create, name='session_create'),
    path('<int:pk>/mark/', views.mark_attendance, name='mark_attendance'),
    path('<int:pk>/', views.session_detail, name='session_detail'),
    path('<int:pk>/delete/', views.session_delete, name='session_delete'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('report/export/', views.export_attendance_csv, name='export_csv'),
    # Student
    path('my/', views.student_attendance, name='student_attendance'),
]
