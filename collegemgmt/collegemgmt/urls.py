from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('role-access/', include('role_access.urls')),
    path('student-management/', include('student_management.urls')),
    path('faculty/', include('faculty.urls')),
    path('academics/', include('academics.urls')),
    path('notifications/', include('core.urls')),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    # JSON/DRF APIs live exclusively under /api/.
    path('api/accounts/', include('accounts.api_urls')),
    path('api/faculty/', include('faculty.api_urls')),
    # Backward-compatible aliases for previous DRF and JSON routes.
    path('api/academics/api/', include('academics.api_urls')),
    path('api/attendance/', include('attendance.api_urls')),
    path('api/core/', include('core.urls', namespace='core_api')),
]

# Serve uploaded media through Django so profile photos work on Vercel too.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
