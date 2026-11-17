from django.urls import path
from . import views

app_name = 'academics'
urlpatterns = [
    path('subjects/', views.manage_subjects, name='subject_management'),
    path('timetable/', views.timetable, name='timetable'),
    path('timetable/new/', views.timetable_create, name='timetable_create'),
    path('timetable/<int:pk>/delete/', views.timetable_delete, name='timetable_delete'),
    path('materials/', views.materials, name='materials'),
    path('materials/upload/', views.material_upload, name='material_upload'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('notices/', views.notices, name='notices'),
    path('notices/new/', views.notice_create, name='notice_create'),
    path('notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),
]
