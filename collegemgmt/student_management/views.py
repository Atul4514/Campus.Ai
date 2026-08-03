from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentProfileForm
from .models import StudentProfile

User = get_user_model()

YEAR_FILTER_CHOICES = [
    ('', 'All Years'),
    ('First Year', 'First Year'),
    ('Second Year', 'Second Year'),
    ('Third Year', 'Third Year'),
    ('Fourth Year', 'Fourth Year'),
]


def _ensure_student_profile(user):
    if user.role == 'student' and not hasattr(user, 'student_profile'):
        StudentProfile.objects.create(user=user)


@login_required(login_url='login_page')
def manage_students(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Only admins can manage students.')
        return redirect('dashboard_page')

    # --- Filters ---
    query = request.GET.get('q', '').strip()
    year_filter = request.GET.get('year', '').strip()
    dept_filter = request.GET.get('dept', '').strip()
    section_filter = request.GET.get('section', '').strip()

    students = User.objects.filter(role='student').select_related('student_profile').order_by('username')

    if query:
        students = students.filter(
            Q(username__icontains=query) |
            Q(full_name__icontains=query) |
            Q(college_id__icontains=query) |
            Q(department__icontains=query)
        )
    if year_filter:
        students = students.filter(student_profile__year=year_filter)
    if dept_filter:
        students = students.filter(department__icontains=dept_filter)
    if section_filter:
        students = students.filter(student_profile__section__iexact=section_filter)

    for student in students:
        _ensure_student_profile(student)

    # --- Pagination ---
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- Stats ---
    all_students = User.objects.filter(role='student')
    total = all_students.count()
    year_counts = {}
    for yc in ['First Year', 'Second Year', 'Third Year', 'Fourth Year']:
        year_counts[yc] = StudentProfile.objects.filter(year=yc).count()

    return render(request, 'accounts/student_management.html', {
        'page_obj': page_obj,
        'students': page_obj,
        'query': query,
        'year_filter': year_filter,
        'dept_filter': dept_filter,
        'section_filter': section_filter,
        'year_choices': YEAR_FILTER_CHOICES,
        'total_students': total,
        'year_counts': year_counts,
    })


@login_required(login_url='login_page')
def student_profile_view(request, student_id=None):
    if request.user.role == 'student':
        student = request.user
        _ensure_student_profile(student)
        profile = student.student_profile
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile was updated successfully.')
                return redirect('student_management:my_profile')
        else:
            form = StudentProfileForm(instance=profile)
        return render(
            request,
            'accounts/student_profile.html',
            {
                'form': form,
                'student': student,
                'profile': profile,
                'is_own_profile': True,
                'can_edit': True,
            },
        )

    if request.user.role not in ['faculty', 'admin']:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('dashboard_page')

    student = get_object_or_404(User, id=student_id, role='student')
    _ensure_student_profile(student)
    profile = student.student_profile
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Academic profile updated for {student.full_name or student.username}.')
            return redirect('student_management:manage_students')
    else:
        form = StudentProfileForm(instance=profile)
    return render(
        request,
        'accounts/student_profile.html',
        {
            'form': form,
            'student': student,
            'profile': profile,
            'is_own_profile': False,
            'can_edit': True,
        },
    )


@login_required(login_url='login_page')
def my_profile(request):
    return student_profile_view(request)


@login_required(login_url='login_page')
def delete_student(request, student_id):
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can delete students.')
        return redirect('dashboard_page')

    student = get_object_or_404(User, id=student_id, role='student')
    if request.method == 'POST':
        name = student.full_name or student.username
        student.delete()
        messages.success(request, f'Student "{name}" has been permanently deleted.')
        return redirect('student_management:manage_students')

    messages.warning(request, 'Invalid request.')
    return redirect('student_management:manage_students')
