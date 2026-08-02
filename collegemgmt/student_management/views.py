from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentProfileForm
from .models import StudentProfile

User = get_user_model()


def _ensure_student_profile(user):
    if user.role == 'student' and not hasattr(user, 'student_profile'):
        StudentProfile.objects.create(user=user)


@login_required(login_url='login_page')
def manage_students(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Only admins can manage students.')
        return redirect('dashboard_page')

    query = request.GET.get('q', '').strip()
    students = User.objects.filter(role='student').order_by('username')
    if query:
        students = students.filter(
            Q(username__icontains=query) |
            Q(full_name__icontains=query) |
            Q(college_id__icontains=query) |
            Q(department__icontains=query)
        )

    for student in students:
        _ensure_student_profile(student)

    return render(request, 'accounts/student_management.html', {'students': students, 'query': query})


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
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Academic profile updated for {student.username}.')
            return redirect('student_management:manage_students')
    else:
        form = StudentProfileForm(instance=profile)
    return render(
        request,
        'accounts/student_profile.html',
        {
            'form': form,
            'student': student,
            'is_own_profile': False,
            'can_edit': True,
        },
    )


@login_required(login_url='login_page')
def my_profile(request):
    return student_profile_view(request)
