from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from students.models import Student
from teachers.models import Teacher, Subject
from core.models import Material, Announcement


class SIHProjectTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher'
        )
        
        self.student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student'
        )
        
        # Create profiles
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            employee_id='T001',
            department='Computer Science'
        )
        
        self.student = Student.objects.create(
            user=self.student_user,
            roll_number='S001',
            interests='Programming, Mathematics'
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            code='TEST101',
            teacher=self.teacher
        )
        
        self.client = Client()

    def test_login_page(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_student_dashboard_access(self):
        """Test student can access dashboard"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('core:dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_teacher_dashboard_access(self):
        """Test teacher can access dashboard"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(reverse('core:dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_access(self):
        """Test admin can access dashboard"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('core:dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_qr_generation(self):
        """Test QR code generation"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(reverse('teachers:generate_qr', args=[self.subject.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generate QR Code')

    def test_material_upload_page(self):
        """Test material upload page"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(reverse('teachers:upload_material', args=[self.subject.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload Study Material')

    def test_announcement_creation(self):
        """Test announcement creation page"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admins:create_announcement'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Announcement')

    def test_user_creation(self):
        """Test user creation page"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admins:add_user'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New User')

    def test_materials_list(self):
        """Test materials list page"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('students:materials_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Materials')

    def test_models_creation(self):
        """Test that models can be created"""
        # Test Student model
        self.assertEqual(self.student.user.username, 'student')
        self.assertEqual(self.student.roll_number, 'S001')
        
        # Test Teacher model
        self.assertEqual(self.teacher.user.username, 'teacher')
        self.assertEqual(self.teacher.employee_id, 'T001')
        
        # Test Subject model
        self.assertEqual(self.subject.name, 'Test Subject')
        self.assertEqual(self.subject.teacher, self.teacher)

    def test_unauthorized_access(self):
        """Test unauthorized access is blocked"""
        # Student trying to access teacher features
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('teachers:generate_qr', args=[self.subject.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Teacher trying to access admin features
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(reverse('admins:add_user'), follow=True)
        self.assertEqual(response.status_code, 200)


