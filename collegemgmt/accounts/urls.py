from django.urls import path, include, reverse_lazy
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import check_college_id
from .views import (
    UserViewSet,
    register_page,
    login_page,
    dashboard_page,
    logout_page,
    CustomPasswordResetView,
)
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # Authentication
    path('register/', register_page, name='register_page'),
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard_page, name='dashboard_page'),
    path('logout/', logout_page, name='logout_page'),
    path('check-college-id/', check_college_id, name='check_college_id'),

    # Forgot Password
    path(
        'password-reset/',
        CustomPasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            form_class=StyledPasswordResetForm,
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done',
    ),

    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            form_class=StyledSetPasswordForm,
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),

    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]