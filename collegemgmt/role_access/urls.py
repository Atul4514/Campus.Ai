from django.urls import path
from .views import manage_roles

app_name = 'role_access'

urlpatterns = [
    path('roles/', manage_roles, name='manage_roles'),
]
