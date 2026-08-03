from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from core.permissions import IsAdmin, IsOwnerOrAdmin, OwnerOrAdminFilterBackend
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from .forms import RegisterForm, LoginForm

User = get_user_model()
from django.contrib.auth.views import PasswordResetView


# ---------- API Views (DRF) ----------

from django.http import JsonResponse
from .models import CollegeIDAllowlist

def check_college_id(request):
    college_id = request.GET.get('college_id', '').strip()
    if not college_id:
        return JsonResponse({'valid': False})
    try:
        entry = CollegeIDAllowlist.objects.get(college_id=college_id)
        if entry.is_used:
            return JsonResponse({'valid': False, 'error': 'already_registered'})
        return JsonResponse({'valid': True, 'role': entry.role, 'department': entry.department})
    except CollegeIDAllowlist.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'not_found'})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [OwnerOrAdminFilterBackend]

    def get_queryset(self):
        user = self.request.user
        if not (user and user.is_authenticated):
            return User.objects.none()
        if getattr(user, 'role', None) == 'admin':
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': 'User registered successfully', 'user': UserSerializer(user).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                auth_login(request, user)
                return Response(
                    {'message': 'Login successful', 'user': UserSerializer(user).data},
                    status=status.HTTP_200_OK
                )
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        auth_logout(request)
        return Response({'message': 'Logout successful'})


# ---------- Template Views (HTML pages) ----------

def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login_page')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard_page')
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url='login_page')
def dashboard_page(request):
    role = request.user.role
    context = {'user': request.user}

    if role == 'admin':
        from .models import CollegeIDAllowlist
        from django.utils import timezone
        from datetime import timedelta

        context['total_students'] = User.objects.filter(role='student').count()
        context['total_faculty'] = User.objects.filter(role='faculty').count()
        context['pending_allowlist'] = CollegeIDAllowlist.objects.filter(is_used=False).count()
        context['new_this_week'] = User.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

    template_map = {
        'student': 'accounts/dashboard_student.html',
        'faculty': 'accounts/dashboard_faculty.html',
        'admin': 'accounts/dashboard_admin.html',
    }
    template = template_map.get(role, 'accounts/dashboard.html')
    return render(request, template, context)

@login_required(login_url='login_page')
def logout_page(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login_page')

from django.contrib.auth.views import PasswordResetView

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        print("=" * 50)
        print("Password Reset Requested")
        print("Email entered:", form.cleaned_data["email"])

        users = list(form.get_users(form.cleaned_data["email"]))
        print("Matching users:", users)

        response = super().form_valid(form)

        print("Password reset process completed.")
        print("=" * 50)

        return response