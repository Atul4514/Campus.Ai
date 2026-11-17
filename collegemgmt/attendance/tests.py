from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from attendance.models import AttendanceSession, AttendanceRecord
from faculty.models import FacultyProfile, SubjectAssignment
from student_management.models import StudentProfile
from academics.models import Subject

User = get_user_model()


class AttendanceModuleTests(TestCase):
    def setUp(self):
        # Create faculty
        self.faculty_user = User.objects.create_user(
            username='prof_smith',
            email='smith@college.edu',
            password='password123',
            full_name='Dr. Smith',
            college_id='FAC001',
            role='faculty',
            department='Computer Science'
        )
        self.faculty_profile, _ = FacultyProfile.objects.get_or_create(user=self.faculty_user)

        # Assign subject to faculty
        self.subject = Subject.objects.create(name='Data Structures', department='Computer Science', semester=3)
        self.assignment = SubjectAssignment.objects.create(
            faculty=self.faculty_profile,
            subject=self.subject,
            section='A'
        )

        # Create students
        self.student1 = User.objects.create_user(
            username='alice',
            email='alice@college.edu',
            password='password123',
            full_name='Alice Wonderland',
            college_id='STU001',
            role='student',
            department='Computer Science'
        )
        self.student1_profile, _ = StudentProfile.objects.get_or_create(user=self.student1)
        self.student1_profile.semester = '3'
        self.student1_profile.section = 'A'
        self.student1_profile.save()

        self.student2 = User.objects.create_user(
            username='bob',
            email='bob@college.edu',
            password='password123',
            full_name='Bob Builder',
            college_id='STU002',
            role='student',
            department='Computer Science'
        )
        self.student2_profile, _ = StudentProfile.objects.get_or_create(user=self.student2)
        self.student2_profile.semester = '3'
        self.student2_profile.section = 'A'
        self.student2_profile.save()

    def test_session_creation_and_stats(self):
        session = AttendanceSession.objects.create(
            subject=self.subject,
            section='A',
            date=date.today(),
            faculty=self.faculty_user,
            topic='Binary Search Trees'
        )
        self.assertEqual(session.total_students, 0)
        self.assertEqual(session.attendance_percentage, 0)

        # Add records
        r1 = AttendanceRecord.objects.create(session=session, student=self.student1, status='P')
        r2 = AttendanceRecord.objects.create(session=session, student=self.student2, status='A')

        self.assertEqual(session.total_students, 2)
        self.assertEqual(session.present_count, 1)
        self.assertEqual(session.attendance_percentage, 50.0)

    def test_student_attendance_view_authenticated(self):
        session = AttendanceSession.objects.create(
            subject=self.subject,
            section='A',
            date=date.today(),
            faculty=self.faculty_user
        )
        AttendanceRecord.objects.create(session=session, student=self.student1, status='P')

        self.client.login(username='alice', password='password123')
        response = self.client.get(reverse('attendance:student_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Structures')
        self.assertContains(response, '100.0%')

    def test_export_csv(self):
        session = AttendanceSession.objects.create(
            subject=self.subject,
            section='A',
            date=date.today(),
            faculty=self.faculty_user
        )
        AttendanceRecord.objects.create(session=session, student=self.student1, status='P')

        self.client.login(username='prof_smith', password='password123')
        response = self.client.get(reverse('attendance:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Alice Wonderland', response.content.decode('utf-8'))
