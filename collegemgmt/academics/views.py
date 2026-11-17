from datetime import date

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.notifications import send_bulk_notification
from faculty.models import SubjectAssignment
from student_management.models import StudentProfile
from .forms import NoticeForm, StudyMaterialForm, SubjectForm, TimetableForm
from .models import Notice, StudyMaterial, Subject, TimetableEntry

User = get_user_model()


def _student_audience_q(profile):
    return Q(subject__department__iexact=profile.user.department, subject__semester=int(profile.semester or 0)) & (Q(section='') | Q(section__iexact=profile.section))


def _can_publish(user, subject, department, semester, section):
    if user.role == 'admin':
        return True
    if user.role != 'faculty':
        return False
    assignments = SubjectAssignment.objects.filter(faculty__user=user, subject=subject)
    if section:
        return assignments.filter(Q(section='') | Q(section__iexact=section)).exists()
    # A blank content section targets every section, so only an explicit
    # all-sections assignment is broad enough to authorize it.
    return assignments.filter(section='').exists()


def _audience_users(department, semester, section):
    profiles = StudentProfile.objects.filter(user__department__iexact=department, semester=str(semester))
    if section:
        profiles = profiles.filter(section__iexact=section)
    return User.objects.filter(pk__in=profiles.values('user_id'))


@login_required(login_url='login_page')
def manage_subjects(request):
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can manage subjects.')
        return redirect('dashboard_page')

    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        subject = form.save()
        messages.success(request, f'{subject.name} was added successfully.')
        return redirect('academics:subject_management')

    return render(request, 'academics/subject_management.html', {
        'form': form,
        'subjects': Subject.objects.order_by('department', 'semester', 'name'),
        'total_subjects': Subject.objects.count(),
    })


@login_required(login_url='login_page')
def timetable(request):
    student_profile = None
    filter_department = ''
    filter_semester = ''
    subjects = None

    if request.user.role == 'student':
        student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)

        # Allow student to filter by department + semester via GET params.
        # Fall back to profile values if params are not supplied.
        filter_department = request.GET.get('department', '').strip() or (request.user.department or '')
        filter_semester = request.GET.get('semester', '').strip() or (student_profile.semester or '')

        if filter_department and filter_semester:
            # Build a temporary profile-like Q filter
            entries = TimetableEntry.objects.filter(
                subject__department__iexact=filter_department,
                subject__semester=int(filter_semester),
            ).filter(Q(section='') | Q(section__iexact=student_profile.section))
            subjects = Subject.objects.filter(
                department__iexact=filter_department,
                semester=int(filter_semester),
            ).order_by('name')
        else:
            entries = TimetableEntry.objects.filter(_student_audience_q(student_profile))
            if student_profile.semester and request.user.department:
                subjects = Subject.objects.filter(
                    department__iexact=request.user.department,
                    semester=int(student_profile.semester),
                ).order_by('name')

    elif request.user.role == 'faculty':
        entries = TimetableEntry.objects.filter(faculty=request.user)
    else:
        entries = TimetableEntry.objects.all()

    # Distinct departments available in the database for the filter dropdown
    dept_choices = Subject.objects.values_list('department', flat=True).distinct().order_by('department')
    semester_choices = range(1, 9)

    return render(request, 'academics/timetable.html', {
        'entries': entries,
        'today': date.today().weekday(),
        'days_of_week': TimetableEntry.DAYS,
        'student_profile': student_profile,
        'filter_department': filter_department,
        'filter_semester': filter_semester,
        'subjects': subjects,
        'dept_choices': dept_choices,
        'semester_choices': semester_choices,
    })


@login_required(login_url='login_page')
def timetable_create(request):
    if request.user.role not in ('admin', 'faculty'):
        return redirect('academics:timetable')
    is_admin = (request.user.role == 'admin')
    form = TimetableForm(request.POST or None, is_admin=is_admin)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        if not is_admin:
            if not _can_publish(request.user, item.subject, item.subject.department, item.subject.semester, item.section):
                form.add_error(None, 'You can schedule only one of your assigned subjects and sections.')
            else:
                item.faculty = request.user
                item.save()
                send_bulk_notification(_audience_users(item.subject.department, item.subject.semester, item.section), 'Timetable updated', f'{item.subject}: {item.get_day_of_week_display()} {item.start_time:%H:%M}–{item.end_time:%H:%M}.', 'timetable_change', '/academics/timetable/')
                messages.success(request, 'Class scheduled and students notified.')
                return redirect('academics:timetable')
        else:
            item.faculty = form.cleaned_data['faculty']
            item.save()
            faculty_name = item.faculty.full_name or item.faculty.username
            send_bulk_notification(_audience_users(item.subject.department, item.subject.semester, item.section), 'Timetable updated', f'{item.subject} assigned to {faculty_name}: {item.get_day_of_week_display()} {item.start_time:%H:%M}–{item.end_time:%H:%M}.', 'timetable_change', '/academics/timetable/')
            messages.success(request, f'Class slot assigned to {faculty_name} and students notified.')
            return redirect('academics:timetable')
    return render(request, 'academics/form.html', {
        'form': form,
        'title': 'Assign Timetable Slot (Faculty & Student)' if is_admin else 'Schedule Class',
    })


@login_required(login_url='login_page')
def materials(request):
    if request.user.role == 'student':
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        items = StudyMaterial.objects.filter(_student_audience_q(profile))
    elif request.user.role == 'faculty':
        items = StudyMaterial.objects.filter(uploaded_by=request.user)
    else:
        items = StudyMaterial.objects.all()

    # Search & subject filter
    q = request.GET.get('q', '').strip()
    subject = request.GET.get('subject', '').strip()
    if q:
        items = items.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(subject__name__icontains=q))
    if subject:
        items = items.filter(subject__name__iexact=subject)

    subjects = items.values_list('subject__name', flat=True).distinct()
    return render(request, 'academics/materials.html', {
        'items': items,
        'subjects': subjects,
        'q': q,
        'selected_subject': subject,
    })


@login_required(login_url='login_page')
def material_upload(request):
    if request.user.role not in ('admin', 'faculty'):
        return redirect('academics:materials')
    form = StudyMaterialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        if not _can_publish(request.user, item.subject, item.subject.department, item.subject.semester, item.section):
            form.add_error(None, 'You can upload notes only for one of your assigned subjects and sections.')
        else:
            item.uploaded_by = request.user
            item.save()
            send_bulk_notification(_audience_users(item.subject.department, item.subject.semester, item.section), 'New study material', f'{item.subject}: {item.title}', 'note_upload', '/academics/materials/')
            messages.success(request, 'Material uploaded and students notified.')
            return redirect('academics:materials')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Upload study material', 'multipart': True})


@login_required(login_url='login_page')
def material_delete(request, pk):
    item = get_object_or_404(StudyMaterial, pk=pk)
    if request.user.role != 'admin' and item.uploaded_by != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('academics:materials')
    if request.method == 'POST':
        item.file.delete(save=False)
        item.delete()
        messages.success(request, 'Study material deleted.')
    return redirect('academics:materials')


@login_required(login_url='login_page')
def notices(request):
    if request.user.role == 'student':
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        items = Notice.objects.filter(_student_audience_q(profile))
    elif request.user.role == 'faculty':
        items = Notice.objects.filter(posted_by=request.user)
    else:
        items = Notice.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        items = items.filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(department__icontains=q))

    pinned_items = items.filter(is_pinned=True)
    other_items = items.filter(is_pinned=False)

    return render(request, 'academics/notices.html', {
        'items': items,
        'pinned_items': pinned_items,
        'other_items': other_items,
        'q': q,
    })


@login_required(login_url='login_page')
def notice_create(request):
    if request.user.role not in ('admin', 'faculty'):
        return redirect('academics:notices')
    form = NoticeForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        if request.user.role == 'faculty' and not SubjectAssignment.objects.filter(faculty__user=request.user, subject__department__iexact=item.department, subject__semester=item.semester, section__in=['', item.section]).exists():
            form.add_error(None, 'You can post notices only to your assigned classes.')
        else:
            item.posted_by = request.user
            item.save()
            send_bulk_notification(_audience_users(item.department, item.semester, item.section), item.title, item.body[:250], 'notice', '/academics/notices/')
            messages.success(request, 'Notice published and students notified.')
            return redirect('academics:notices')
    return render(request, 'academics/form.html', {'form': form, 'title': 'Post notice', 'multipart': True})


@login_required(login_url='login_page')
def notice_delete(request, pk):
    item = get_object_or_404(Notice, pk=pk)
    if request.user.role != 'admin' and item.posted_by != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('academics:notices')
    if request.method == 'POST':
        if item.attachment:
            item.attachment.delete(save=False)
        item.delete()
        messages.success(request, 'Notice deleted.')
    return redirect('academics:notices')


@login_required(login_url='login_page')
def timetable_delete(request, pk):
    item = get_object_or_404(TimetableEntry, pk=pk)
    if request.user.role != 'admin' and item.faculty != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('academics:timetable')
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Timetable slot removed.')
    return redirect('academics:timetable')
