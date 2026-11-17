from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class RoleAccessManagementTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='adminuser',
            password='testpass123',
            college_id='ADM001',
            role='admin',
            full_name='Admin User',
        )
        self.student = User.objects.create_user(
            username='studentuser',
            password='testpass123',
            college_id='STU001',
            role='student',
            full_name='Student User',
        )

    def test_admin_can_open_role_management_page(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('role_access:manage_roles'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Role & Access Management')

    def test_admin_can_update_user_role(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('role_access:manage_roles'),
            {'user_id': self.student.id, 'role': 'faculty'},
        )
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.role, 'faculty')

    def test_admin_can_open_student_management_page(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('student_management:manage_students'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student Management')

    def test_non_admin_cannot_access_management_page(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('role_access:manage_roles'))
        self.assertEqual(response.status_code, 302)

    def test_faculty_dashboard_renders(self):
        faculty = get_user_model().objects.create_user(
            username='facultyuser',
            password='testpass123',
            college_id='FAC001',
            role='faculty',
            full_name='Faculty User',
        )
        self.client.force_login(faculty)
        response = self.client.get(reverse('dashboard_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Faculty Dashboard')

    def test_student_dashboard_renders(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('dashboard_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student Dashboard')

    def test_admin_dashboard_renders(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
