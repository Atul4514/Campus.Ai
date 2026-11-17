from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from faculty.models import FacultyProfile


class FacultyDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='password123', full_name='Admin User',
            college_id='ADM001', role='admin',
        )
        self.faculty = User.objects.create_user(
            username='faculty1', password='password123', full_name='Faculty Member',
            college_id='FAC001', role='faculty',
        )

    def test_admin_can_view_faculty_management(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('faculty:manage_faculty_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Faculty Member')

    def test_management_repairs_missing_profile_and_counts_all_faculty_users(self):
        FacultyProfile.objects.filter(user=self.faculty).delete()

        self.client.force_login(self.admin)
        response = self.client.get(reverse('faculty:manage_faculty_page'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Faculty Member')
        self.assertEqual(response.context['total_faculty'], 1)
        self.assertTrue(FacultyProfile.objects.filter(user=self.faculty).exists())

    def test_student_cannot_view_faculty_management(self):
        student = User.objects.create_user(
            username='student1', password='password123', full_name='Student User',
            college_id='STD001', role='student',
        )
        self.client.force_login(student)
        response = self.client.get(reverse('faculty:manage_faculty_page'))
        self.assertEqual(response.status_code, 302)

    def test_faculty_profile_api_is_scoped_to_owner(self):
        other_user = User.objects.create_user(
            username='faculty2', password='password123', full_name='Other Faculty',
            college_id='FAC002', role='faculty',
        )
        own_profile = FacultyProfile.objects.get(user=self.faculty)
        other_profile = FacultyProfile.objects.get(user=other_user)

        self.client.force_login(self.faculty)
        response = self.client.get('/api/faculty/profiles/')

        self.assertEqual(response.status_code, 200)
        returned_ids = {item['id'] for item in response.json()}
        self.assertIn(own_profile.pk, returned_ids)
        self.assertNotIn(other_profile.pk, returned_ids)

    def test_admin_can_list_all_faculty_profiles(self):
        FacultyProfile.objects.get(user=self.faculty)
        self.client.force_login(self.admin)

        response = self.client.get('/api/faculty/profiles/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), FacultyProfile.objects.count())
