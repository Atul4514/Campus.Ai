from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from academics.models import Subject
from academics.views import _can_publish
from faculty.models import FacultyProfile, SubjectAssignment


class SubjectPublishingAuthorizationTests(TestCase):
    def setUp(self):
        self.faculty = User.objects.create_user(
            username='section_a_faculty', password='test-pass-123',
            full_name='Section A Faculty', college_id='FAC-AUTH-1', role='faculty',
        )
        self.profile = FacultyProfile.objects.get(user=self.faculty)
        self.subject = Subject.objects.create(
            name='Data Structures', department='Computer Science', semester=3,
        )

    def test_section_assignment_allows_only_same_section_content(self):
        SubjectAssignment.objects.create(faculty=self.profile, subject=self.subject, section='A')

        self.assertTrue(_can_publish(self.faculty, self.subject, '', 0, 'A'))
        self.assertFalse(_can_publish(self.faculty, self.subject, '', 0, ''))
        self.assertFalse(_can_publish(self.faculty, self.subject, '', 0, 'B'))

    def test_all_sections_assignment_allows_any_section(self):
        SubjectAssignment.objects.create(faculty=self.profile, subject=self.subject, section='')

        self.assertTrue(_can_publish(self.faculty, self.subject, '', 0, ''))
        self.assertTrue(_can_publish(self.faculty, self.subject, '', 0, 'A'))


class SubjectManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='subject_admin', password='test-pass-123',
            full_name='Subject Admin', college_id='SUBJECT-ADMIN', role='admin',
        )
        self.faculty = User.objects.create_user(
            username='subject_faculty', password='test-pass-123',
            full_name='Subject Faculty', college_id='SUBJECT-FACULTY', role='faculty',
        )

    def test_admin_can_create_subject_from_subject_management_page(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse('academics:subject_management'), {
            'name': 'Operating Systems',
            'department': 'Computer Science',
            'semester': 4,
        })

        self.assertRedirects(response, reverse('academics:subject_management'))
        subject = Subject.objects.get(name='Operating Systems')
        self.assertEqual(subject.department, 'Computer Science')
        self.assertEqual(subject.semester, 4)

    def test_non_admin_cannot_open_subject_management(self):
        self.client.force_login(self.faculty)

        response = self.client.get(reverse('academics:subject_management'))

        self.assertRedirects(response, reverse('dashboard_page'))
