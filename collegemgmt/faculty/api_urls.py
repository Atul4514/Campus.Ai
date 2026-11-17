from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FacultyProfileViewSet

router = DefaultRouter()
router.register('profiles', FacultyProfileViewSet, basename='faculty-profile')

urlpatterns = [path('', include(router.urls))]
