from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, check_college_id

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('check-college-id/', check_college_id, name='check_college_id_api'),
]
