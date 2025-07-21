from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, UserProfile


class UserModelTests(TestCase):
    """Tests for the User model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Test that a user can be created."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.user_type, 'customer')  # Default value
        self.assertTrue(self.user.check_password('testpassword'))
    
    def test_user_profile_creation(self):
        """Test that a UserProfile is automatically created for a new user."""
        self.assertIsNotNone(self.user.profile)
        self.assertEqual(self.user.profile.loyalty_points, 0)  # Default value
        self.assertEqual(self.user.profile.loyalty_level, 'standard')  # Default value


class UserAPITests(APITestCase):
    """Tests for the User API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_detail(self):
        """Test retrieving a user's details."""
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_user_profile(self):
        """Test updating a user's profile."""
        url = reverse('user-profile', args=[self.user.id])
        data = {
            'bio': 'This is a test bio',
            'preferences': {'theme': 'dark'}
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'This is a test bio')
        self.assertEqual(self.user.profile.preferences, {'theme': 'dark'})
    
    def test_register_user(self):
        """Test registering a new user."""
        self.client.logout()
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword',
            'password_confirm': 'newpassword',
            'user_type': 'customer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())