from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Skills, Author, Location, JobPost
import json

# Create your tests here.

class JobPostModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.author = Author.objects.create(
            user=self.user,
            company='Test Company',
            designation='Test Developer'
        )
        self.location = Location.objects.create(
            street='123 Test St',
            city='Test City',
            state='TS',
            country='Test Country',
            zip='12345'
        )
        self.skill = Skills.objects.create(name='Python')
        
    def test_jobpost_creation(self):
        """Test JobPost model creation"""
        job = JobPost.objects.create(
            title='Test Job',
            description='Test Description',
            salary=50000,
            author=self.author,
            location=self.location
        )
        job.skills.add(self.skill)
        
        self.assertEqual(job.title, 'Test Job')
        self.assertEqual(job.salary, 50000)
        self.assertEqual(job.author, self.author)
        self.assertEqual(job.location, self.location)
        self.assertIn(self.skill, job.skills.all())
        self.assertIsNotNone(job.slug)
        
    def test_jobpost_slug_generation(self):
        """Test automatic slug generation"""
        job = JobPost.objects.create(
            title='Test Job Title',
            description='Test Description',
            salary=50000,
            author=self.author,
            location=self.location
        )
        self.assertEqual(job.slug, 'test-job-title')
        
    def test_jobpost_str_method(self):
        """Test JobPost string representation"""
        job = JobPost.objects.create(
            title='Test Job',
            description='Test Description',
            salary=50000,
            author=self.author,
            location=self.location
        )
        self.assertEqual(str(job), 'Test Job')


class JobPostViewTest(TestCase):
    def setUp(self):
        """Set up test data for views"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.author = Author.objects.create(
            user=self.user,
            company='Test Company',
            designation='Test Developer'
        )
        self.location = Location.objects.create(
            street='123 Test St',
            city='Test City',
            state='TS',
            country='Test Country',
            zip='12345'
        )
        self.skill = Skills.objects.create(name='Python')
        self.job = JobPost.objects.create(
            title='Test Job',
            description='Test Description',
            salary=50000,
            author=self.author,
            location=self.location
        )
        self.job.skills.add(self.skill)
        
    def test_jobpost_list_view(self):
        """Test job post list API"""
        response = self.client.get(reverse('jobpost_list'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('jobs', data)
        self.assertEqual(len(data['jobs']), 1)
        self.assertEqual(data['jobs'][0]['title'], 'Test Job')
        
    def test_jobpost_detail_view(self):
        """Test job post detail API"""
        response = self.client.get(reverse('jobpost_detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'Test Job')
        self.assertEqual(data['salary'], 50000)
        
    def test_jobpost_detail_not_found(self):
        """Test job post detail API with invalid ID"""
        response = self.client.get(reverse('jobpost_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
    def test_skills_list_view(self):
        """Test skills list API"""
        response = self.client.get(reverse('skills_list'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('skills', data)
        self.assertIn('Python', data['skills'])
