import csv
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from faculty.models import SubjectAssignment
from student_management.models import StudentProfile
from .forms import AttendanceSessionForm
from .models import AttendanceRecord, AttendanceSession

User = get_user_model()


# ──────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────

def _get_session_students(session):
    """Return queryset of student Users matching a session's dept/sem/section."""
    profiles = StudentProfile.objects.filter(
        user__department__iexact=session.subject.department,
        semester=str(session.subject.semester),
    )
    if session.section:
        profiles = profiles.filter(section__iexact=session.section)
    return User.objects.filter(
        pk__in=profiles.values('user_id'),
        role='student',
    ).order_by('full_name')


def _can_manage_session(user, session):
    """Faculty can only manage sessions they created; admin can manage all."""
    if user.role == 'admin':
        return True
    return session.faculty_id == user.pk


def _faculty_subjects(user):
    """Return SubjectAssignment queryset for a faculty user."""
    return SubjectAssignment.objects.filter(faculty__user=user)


# ──────────────────────────────────────────────────────
# Session list (faculty / admin)
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def session_list(request):
    if request.user.role not in ('faculty', 'admin'):
        return redirect('attendance:student_attendance')

    if request.user.role == 'admin':
        sessions = AttendanceSession.objects.select_related('faculty').all()
    else:
        sessions = AttendanceSession.objects.filter(faculty=request.user)

    # Summary stats
    total_sessions = sessions.count()
    total_records = AttendanceRecord.objects.filter(session__in=sessions)
    present_records = total_records.filter(status__in=['P', 'L'])
    overall_pct = 0
    if total_records.count() > 0:
        overall_pct = round((present_records.count() / total_records.count()) * 100, 1)

    # Top 5 students with highest attendance
    student_summary = defaultdict(lambda: {'total': 0, 'present': 0, 'name': '', 'college_id': '', 'dept': '', 'sem': ''})
    for rec in total_records.select_related('student', 'session__subject'):
        key = rec.student_id
        student_summary[key]['name'] = rec.student.full_name or rec.student.username
        student_summary[key]['college_id'] = getattr(rec.student, 'college_id', '') or ''
        if rec.session and rec.session.subject:
            student_summary[key]['dept'] = rec.session.subject.department
            student_summary[key]['sem'] = rec.session.subject.semester
        student_summary[key]['total'] += 1
        if rec.status in ('P', 'L'):
            student_summary[key]['present'] += 1

    top_students = []
    for uid, data in student_summary.items():
        if data['total'] > 0:
            pct = round((data['present'] / data['total']) * 100, 1)
            top_students.append({
                'name': data['name'],
                'college_id': data['college_id'],
                'department': data['dept'],
                'semester': data['sem'],
                'total': data['total'],
                'present': data['present'],
                'percentage': pct,
            })
    top_students.sort(key=lambda x: (x['percentage'], x['present']), reverse=True)
    top_students = top_students[:5]

    return render(request, 'attendance/session_list.html', {
        'sessions': sessions,
        'total_sessions': total_sessions,
        'overall_pct': overall_pct,
        'total_students_marked': total_records.count(),
        'top_students': top_students,
    })


# ──────────────────────────────────────────────────────
# Create session
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def session_create(request):
    if request.user.role not in ('faculty', 'admin'):
        return redirect('attendance:student_attendance')

    from academics.models import Subject
    assignments = SubjectAssignment.objects.select_related('subject', 'faculty__user')
    if request.user.role == 'faculty':
        assignments = assignments.filter(faculty__user=request.user)
        subject_options = Subject.objects.filter(
            faculty_assignments__faculty__user=request.user,
        ).distinct().order_by('department', 'semester', 'name')
    else:
        subject_options = Subject.objects.order_by('department', 'semester', 'name')
        assignments = assignments.filter(subject__in=subject_options)

    form = AttendanceSessionForm(request.POST or None)
    form.fields['subject'].queryset = subject_options

    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        # Check faculty is allowed to mark for this subject/dept/sem
        if request.user.role == 'faculty':
            allowed = SubjectAssignment.objects.filter(
                faculty__user=request.user,
                subject=session.subject,
                section__in=['', session.section],
            ).exists()
            if not allowed:
                form.add_error(None, 'You are not assigned to teach this subject/class.')
            else:
                session.faculty = request.user
                session.save()
                messages.success(request, 'Session created. Now mark attendance below.')
                return redirect('attendance:mark_attendance', pk=session.pk)
        else:
            session.faculty = request.user
            session.save()
            messages.success(request, 'Session created. Now mark attendance below.')
            return redirect('attendance:mark_attendance', pk=session.pk)

    return render(request, 'attendance/session_create.html', {
        'form': form,
        'subjects': assignments,
        'subject_metadata': list(subject_options.values('id', 'department', 'semester')),
    })


# ──────────────────────────────────────────────────────
# Mark attendance (bulk)
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def mark_attendance(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    if not _can_manage_session(request.user, session):
        messages.error(request, 'You do not have permission to mark this session.')
        return redirect('attendance:session_list')

    students = _get_session_students(session)

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.pk}', 'A')
            remarks = request.POST.get(f'remarks_{student.pk}', '').strip()
            AttendanceRecord.objects.update_or_create(
                session=session,
                student=student,
                defaults={'status': status, 'remarks': remarks},
            )
        messages.success(request, 'Attendance saved successfully.')
        return redirect('attendance:session_detail', pk=session.pk)

    # Pre-fill existing records
    existing = {r.student_id: r for r in session.records.all()}

    student_data = []
    for s in students:
        rec = existing.get(s.pk)
        student_data.append({
            'user': s,
            'status': rec.status if rec else 'A',
            'remarks': rec.remarks if rec else '',
        })

    return render(request, 'attendance/mark_attendance.html', {
        'session': session,
        'student_data': student_data,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
    })


# ──────────────────────────────────────────────────────
# Session detail / view breakdown
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def session_detail(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    if not _can_manage_session(request.user, session):
        messages.error(request, 'Access denied.')
        return redirect('attendance:session_list')

    records = session.records.select_related('student').all()
    counts = {
        'P': records.filter(status='P').count(),
        'A': records.filter(status='A').count(),
        'L': records.filter(status='L').count(),
        'E': records.filter(status='E').count(),
    }

    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'records': records,
        'counts': counts,
    })


# ──────────────────────────────────────────────────────
# Delete session
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def session_delete(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    if not _can_manage_session(request.user, session):
        messages.error(request, 'Access denied.')
        return redirect('attendance:session_list')
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Session deleted.')
    return redirect('attendance:session_list')


# ──────────────────────────────────────────────────────
# Student: My Attendance
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def student_attendance(request):
    if request.user.role != 'student':
        return redirect('attendance:session_list')

    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    sem = int(profile.semester or 0)

    sessions = AttendanceSession.objects.filter(
        subject__department__iexact=request.user.department,
        subject__semester=sem,
    ).filter(
        Q(section='') | Q(section__iexact=profile.section)
    )

    records = AttendanceRecord.objects.filter(
        session__in=sessions,
        student=request.user,
    ).select_related('session')

    # Subject-wise breakdown
    subject_stats = defaultdict(lambda: {'total': 0, 'present': 0})
    for rec in records:
        subj = rec.session.subject.name
        subject_stats[subj]['total'] += 1
        if rec.status in ('P', 'L'):
            subject_stats[subj]['present'] += 1

    subject_list = []
    for subj, data in subject_stats.items():
        pct = round((data['present'] / data['total']) * 100, 1) if data['total'] else 0
        subject_list.append({
            'subject': subj,
            'total': data['total'],
            'present': data['present'],
            'absent': data['total'] - data['present'],
            'percentage': pct,
            'status_class': 'success' if pct >= 75 else ('warning' if pct >= 60 else 'danger'),
        })

    subject_list.sort(key=lambda x: x['subject'])

    # Recent records for calendar-like view (last 30)
    recent_records = records.order_by('-session__date')[:30]

    overall_total = sum(s['total'] for s in subject_list)
    overall_present = sum(s['present'] for s in subject_list)
    overall_pct = round((overall_present / overall_total) * 100, 1) if overall_total else 0

    return render(request, 'attendance/student_attendance.html', {
        'subject_list': subject_list,
        'recent_records': recent_records,
        'overall_pct': overall_pct,
        'overall_total': overall_total,
        'overall_present': overall_present,
        'profile': profile,
    })


# ──────────────────────────────────────────────────────
# Admin: Full attendance report
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def attendance_report(request):
    if request.user.role not in ('admin', 'faculty'):
        return redirect('attendance:student_attendance')

    dept = request.GET.get('department', '').strip()
    sem = request.GET.get('semester', '').strip()
    section = request.GET.get('section', '').strip()
    subject = request.GET.get('subject', '').strip()

    sessions = AttendanceSession.objects.all()
    if request.user.role == 'faculty':
        sessions = sessions.filter(faculty=request.user)
    if dept:
        sessions = sessions.filter(subject__department__icontains=dept)
    if sem:
        sessions = sessions.filter(subject__semester=int(sem))
    if section:
        sessions = sessions.filter(section__icontains=section)
    if subject:
        sessions = sessions.filter(subject__name__icontains=subject)

    # Per-student summary
    records = AttendanceRecord.objects.filter(session__in=sessions).select_related('student', 'session')

    student_summary = defaultdict(lambda: {'total': 0, 'present': 0, 'name': '', 'dept': '', 'sem': ''})
    for rec in records:
        key = rec.student_id
        student_summary[key]['name'] = rec.student.full_name or rec.student.username
        student_summary[key]['college_id'] = rec.student.college_id
        student_summary[key]['dept'] = rec.session.subject.department
        student_summary[key]['sem'] = rec.session.subject.semester
        student_summary[key]['total'] += 1
        if rec.status in ('P', 'L'):
            student_summary[key]['present'] += 1

    report_rows = []
    for uid, data in student_summary.items():
        pct = round((data['present'] / data['total']) * 100, 1) if data['total'] else 0
        report_rows.append({
            'student_id': uid,
            'name': data['name'],
            'college_id': data['college_id'],
            'department': data['dept'],
            'semester': data['sem'],
            'total': data['total'],
            'present': data['present'],
            'absent': data['total'] - data['present'],
            'percentage': pct,
            'status_class': 'success' if pct >= 75 else ('warning' if pct >= 60 else 'danger'),
        })
    report_rows.sort(key=lambda x: x['name'])

    # Top 5 students with highest attendance
    top_students = sorted(report_rows, key=lambda x: (x['percentage'], x['present']), reverse=True)[:5]

    # Available filter options
    all_sessions = AttendanceSession.objects.all()
    if request.user.role == 'faculty':
        all_sessions = all_sessions.filter(faculty=request.user)
    departments = all_sessions.values_list('subject__department', flat=True).distinct()
    subjects = all_sessions.values_list('subject__name', flat=True).distinct()

    return render(request, 'attendance/report.html', {
        'report_rows': report_rows,
        'sessions': sessions,
        'departments': departments,
        'subjects_list': subjects,
        'filters': {'department': dept, 'semester': sem, 'section': section, 'subject': subject},
        'top_students': top_students,
    })


# ──────────────────────────────────────────────────────
# CSV Export
# ──────────────────────────────────────────────────────

@login_required(login_url='login_page')
def export_attendance_csv(request):
    if request.user.role not in ('admin', 'faculty'):
        return redirect('attendance:student_attendance')

    dept = request.GET.get('department', '').strip()
    sem = request.GET.get('semester', '').strip()
    section = request.GET.get('section', '').strip()
    subject = request.GET.get('subject', '').strip()

    sessions = AttendanceSession.objects.all()
    if request.user.role == 'faculty':
        sessions = sessions.filter(faculty=request.user)
    if dept:
        sessions = sessions.filter(subject__department__icontains=dept)
    if sem:
        try:
            sessions = sessions.filter(subject__semester=int(sem))
        except ValueError:
            pass
    if section:
        sessions = sessions.filter(section__icontains=section)
    if subject:
        sessions = sessions.filter(subject__name__icontains=subject)

    records = AttendanceRecord.objects.filter(
        session__in=sessions
    ).select_related('student', 'session').order_by('session__date', 'student__full_name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'College ID', 'Department', 'Semester', 'Section', 'Subject', 'Date', 'Status', 'Remarks'])
    for rec in records:
        writer.writerow([
            rec.student.full_name or rec.student.username,
            rec.student.college_id,
            rec.session.subject.department,
            rec.session.subject.semester,
            rec.session.section,
            rec.session.subject.name,
            rec.session.date,
            rec.get_status_display(),
            rec.remarks,
        ])

    return response
