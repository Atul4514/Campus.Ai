from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('page/', views.notification_page, name='notification_page'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('<int:notif_id>/read/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]
