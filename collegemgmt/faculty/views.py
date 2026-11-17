from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.mixins import AccessLogMixin
from core.permissions import IsAdmin, IsOwnerOrAdmin
from core.viewsets import OwnerOrAdminQuerysetMixin

from .forms import FacultyProfileEditForm, SubjectAssignmentForm
from .models import FacultyProfile, SubjectAssignment
from .serializers import FacultyProfileSerializer, FacultyProfileUpdateSerializer

User = get_user_model()


# ─── DRF API ──────────────────────────────────────────────────────────────────

class FacultyProfileViewSet(OwnerOrAdminQuerysetMixin, AccessLogMixin, viewsets.ModelViewSet):
    log_model_name = "FacultyProfile"
    queryset = FacultyProfile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return FacultyProfileUpdateSerializer
        return FacultyProfileSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]


# ─── Access helpers ────────────────────────────────────────────────────────────

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'
 
def is_faculty_or_admin(user):
    return user.is_authenticated and user.role in ('faculty', 'admin')


# ─── Admin: Manage Faculty ─────────────────────────────────────────────────────

@login_required(login_url='login_page')
@user_passes_test(is_admin, login_url='dashboard_page')
def manage_faculty_page(request):
    query = request.GET.get('q', '').strip()
    dept_filter = request.GET.get('dept', '').strip()

    # A faculty user may have been created by a role change or older import
    # without the profile normally created during registration. Repair these
    # rows so every faculty account appears in management.
    faculty_user_ids = User.objects.filter(role='faculty').values_list('id', flat=True)
    profiled_user_ids = set(
        FacultyProfile.objects.filter(user_id__in=faculty_user_ids)
        .values_list('user_id', flat=True)
    )
    FacultyProfile.objects.bulk_create(
        [
            FacultyProfile(user_id=user_id)
            for user_id in faculty_user_ids
            if user_id not in profiled_user_ids
        ],
        ignore_conflicts=True,
    )

    faculty_qs = (
        FacultyProfile.objects
        .select_related('user')
        .prefetch_related('subject_assignments')
        .order_by('user__full_name')
    )

    if query:
        faculty_qs = faculty_qs.filter(
            Q(user__full_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__college_id__icontains=query) |
            Q(employee_id__icontains=query)
        )
    if dept_filter:
        faculty_qs = faculty_qs.filter(user__department__icontains=dept_filter)

    paginator = Paginator(faculty_qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'faculty/manage_faculty.html', {
        'page_obj': page_obj,
        'query': query,
        'dept_filter': dept_filter,
        'total_faculty': User.objects.filter(role='faculty').count(),
    })


@login_required(login_url='login_page')
@user_passes_test(is_admin, login_url='dashboard_page')
def edit_faculty_page(request, faculty_id):
    """Admin edits any faculty profile + manages subject assignments."""
    profile = get_object_or_404(FacultyProfile, pk=faculty_id)

    if request.method == 'POST' and request.POST.get('form_type') == 'profile':
        form = FacultyProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Profile updated for {profile.user.full_name or profile.user.username}.')
            return redirect('manage_faculty_page')
    else:
        form = FacultyProfileEditForm(instance=profile)

    # Handle subject assignment add
    sa_form = SubjectAssignmentForm()
    if request.method == 'POST' and request.POST.get('form_type') == 'subject':
        sa_form = SubjectAssignmentForm(request.POST)
        if sa_form.is_valid():
            sa = sa_form.save(commit=False)
            sa.faculty = profile
            sa.save()
            messages.success(request, f'Subject "{sa.subject}" assigned.')
            return redirect('faculty:edit_faculty', faculty_id=faculty_id)

    # Handle subject assignment delete
    if request.method == 'POST' and request.POST.get('form_type') == 'delete_subject':
        sa_id = request.POST.get('sa_id')
        SubjectAssignment.objects.filter(pk=sa_id, faculty=profile).delete()
        messages.success(request, 'Subject removed.')
        return redirect('faculty:edit_faculty', faculty_id=faculty_id)

    return render(request, 'faculty/edit_faculty.html', {
        'profile': profile,
        'form': form,
        'sa_form': sa_form,
        'assignments': profile.subject_assignments.all(),
    })


@login_required(login_url='login_page')
@user_passes_test(is_admin, login_url='dashboard_page')
def delete_faculty_page(request, faculty_id):
    profile = get_object_or_404(FacultyProfile, pk=faculty_id)
    if request.method == 'POST':
        name = profile.user.full_name or profile.user.username
        profile.user.delete()   # cascades to FacultyProfile
        messages.success(request, f'Faculty "{name}" deleted.')
        return redirect('manage_faculty_page')
    messages.warning(request, 'Invalid request.')
    return redirect('manage_faculty_page')


# ─── Faculty: My Profile (edit own) ───────────────────────────────────────────

@login_required(login_url='login_page')
def my_faculty_profile_page(request):
    if request.user.role not in ('faculty', 'admin'):
        return redirect('dashboard_page')

    profile, _ = FacultyProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = FacultyProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('faculty:my_faculty_profile_page')
    else:
        form = FacultyProfileEditForm(instance=profile)

    return render(request, 'faculty/my_profile.html', {
        'profile': profile,
        'form': form,
    })


# ─── Faculty: My Students ─────────────────────────────────────────────────────

@login_required(login_url='login_page')
def my_students_page(request):
    if request.user.role not in ('faculty', 'admin'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard_page')

    dept = request.user.department if request.user.role == 'faculty' else request.GET.get('dept', '').strip()

    section_filter = request.GET.get('section', '').strip()
    semester_filter = request.GET.get('semester', '').strip()

    students = (
        User.objects
        .filter(role='student')
        .select_related('student_profile')
        .order_by('full_name')
    )

    if dept:
        students = students.filter(department__iexact=dept)
    if section_filter:
        students = students.filter(student_profile__section__iexact=section_filter)
    if semester_filter:
        students = students.filter(student_profile__semester=semester_filter)

    paginator = Paginator(students, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'faculty/my_students.html', {
        'page_obj': page_obj,
        'dept': dept,
        'section_filter': section_filter,
        'semester_filter': semester_filter,
        'total': students.count(),
    })
