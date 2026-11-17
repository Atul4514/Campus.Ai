from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from academics.models import Subject, TimetableEntry
from attendance.models import AttendanceRecord, AttendanceSession
from faculty.models import FacultyProfile, SubjectAssignment
from student_management.models import StudentProfile


User = get_user_model()


class CampusWorkflowEndToEndTests(TestCase):
    """Exercise the student, faculty, timetable, and attendance flow together."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='workflow_admin', password='TestPass123!',
            full_name='Workflow Admin', college_id='WF-ADMIN', role='admin',
        )
        self.faculty = []
        for number in range(1, 4):
            user = User.objects.create_user(
                username=f'workflow_faculty_{number}', password='TestPass123!',
                full_name=f'Workflow Faculty {number}', college_id=f'WF-FAC-{number}',
                role='faculty', department='Computer Science',
            )
            self.faculty.append(user)

        self.students = []
        for number in range(1, 11):
            student = User.objects.create_user(
                username=f'workflow_student_{number}', password='TestPass123!',
                full_name=f'Workflow Student {number}', college_id=f'WF-STU-{number}',
                role='student', department='Computer Science',
            )
            profile = StudentProfile.objects.get(user=student)
            profile.semester = '3'
            profile.section = 'A'
            profile.save()
            self.students.append(student)

        self.subjects = []
        for number, faculty in enumerate(self.faculty, start=1):
            subject = Subject.objects.create(
                name=f'Workflow Subject {number}', department='Computer Science', semester=3,
            )
            self.subjects.append(subject)
            SubjectAssignment.objects.create(
                faculty=FacultyProfile.objects.get(user=faculty), subject=subject, section='A',
            )
            TimetableEntry.objects.create(
                subject=subject, faculty=faculty, section='A', day_of_week=number - 1,
                start_time=time(9, 0), end_time=time(10, 0), room=f'WF-{number}',
            )

    def test_three_roles_can_view_their_timetable(self):
        for user, expected_count in (
            (self.admin, 3), (self.faculty[0], 1), (self.students[0], 3),
        ):
            with self.subTest(role=user.role):
                self.client.force_login(user)
                response = self.client.get(reverse('academics:timetable'))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['entries']), expected_count)

    def test_faculty_creates_session_and_marks_ten_students(self):
        faculty = self.faculty[0]
        subject = self.subjects[0]
        self.client.force_login(faculty)

        response = self.client.post(reverse('attendance:session_create'), {
            'subject': subject.pk,
            'section': 'A',
            'date': date.today().isoformat(),
            'topic': 'Workflow attendance check',
        })
        self.assertEqual(response.status_code, 302)
        session = AttendanceSession.objects.get(topic='Workflow attendance check')
        self.assertEqual(session.faculty, faculty)

        response = self.client.get(reverse('attendance:mark_attendance', args=[session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['student_data']), 10)

        attendance_payload = {
            f'status_{student.pk}': ('P' if index < 8 else 'A')
            for index, student in enumerate(self.students)
        }
        response = self.client.post(
            reverse('attendance:mark_attendance', args=[session.pk]), attendance_payload,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AttendanceRecord.objects.filter(session=session).count(), 10)
        self.assertEqual(session.records.filter(status='P').count(), 8)
        self.assertEqual(session.attendance_percentage, 80.0)

        response = self.client.get(reverse('attendance:session_detail', args=[session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['counts']['P'], 8)
        self.assertEqual(response.context['counts']['A'], 2)

        self.client.force_login(self.students[0])
        response = self.client.get(reverse('attendance:student_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workflow Subject 1')
        self.assertContains(response, '100.0%')

        self.client.force_login(self.admin)
        response = self.client.get(reverse('attendance:attendance_report'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['report_rows']), 10)
