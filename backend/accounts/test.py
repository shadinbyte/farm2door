from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import CustomerProfile, FarmerProfile, User, UserProfile


class UserRegistrationTests(APITestCase):
    """Test user registration"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")

    def test_register_customer(self):
        """Test customer registration"""
        data = {
            "username": "testcustomer",
            "email": "customer@test.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "phone_number": "+8801712345678",
            "user_type": "customer",
            "first_name": "Test",
            "last_name": "Customer",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testcustomer").exists())
        self.assertIn("tokens", response.data)

        # Check if profiles were created
        user = User.objects.get(username="testcustomer")
        self.assertTrue(hasattr(user, "profile"))
        self.assertTrue(hasattr(user, "customer_profile"))

    def test_register_farmer(self):
        """Test farmer registration"""
        data = {
            "username": "testfarmer",
            "email": "farmer@test.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "phone_number": "+8801812345678",
            "user_type": "farmer",
            "first_name": "Test",
            "last_name": "Farmer",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="testfarmer")
        self.assertTrue(hasattr(user, "farmer_profile"))

    def test_register_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "TestPass123!",
            "password_confirm": "DifferentPass123!",
            "phone_number": "+8801912345678",
            "user_type": "customer",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_register_with_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            username="existing",
            email="duplicate@test.com",
            password="pass123",
            phone_number="+8801612345678",
            user_type="customer",
        )

        data = {
            "username": "newuser",
            "email": "duplicate@test.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "phone_number": "+8801712345679",
            "user_type": "customer",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """Test user login"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("login")

        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="TestPass123!",
            phone_number="+8801712345678",
            user_type="customer",
        )

    def test_login_success(self):
        """Test successful login"""
        data = {"username": "testuser", "password": "TestPass123!"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"username": "testuser", "password": "WrongPassword"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()

        data = {"username": "testuser", "password": "TestPass123!"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTests(APITestCase):
    """Test user profile"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="TestPass123!",
            phone_number="+8801712345678",
            user_type="customer",
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse("profile")

    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertIn("profile", response.data)
        self.assertIn("customer_profile", response.data)

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeTests(APITestCase):
    """Test password change"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="OldPass123!",
            phone_number="+8801712345678",
            user_type="customer",
        )
        self.client.force_authenticate(user=self.user)
        self.change_password_url = reverse("change_password")

    def test_change_password_success(self):
        """Test successful password change"""
        data = {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123!"))

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        data = {
            "old_password": "WrongOldPass123!",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Test password change with mismatched new passwords"""
        data = {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "new_password_confirm": "DifferentPass123!",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ModelTests(TestCase):
    """Test models"""

    def test_user_creation(self):
        """Test user model creation"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="TestPass123!",
            phone_number="+8801712345678",
            user_type="customer",
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.user_type, "customer")
        self.assertTrue(user.check_password("TestPass123!"))

    def test_farmer_profile_creation(self):
        """Test farmer profile creation"""
        user = User.objects.create_user(
            username="farmer",
            email="farmer@test.com",
            password="TestPass123!",
            phone_number="+8801812345678",
            user_type="farmer",
        )

        # Signal should auto-create profiles
        self.assertTrue(hasattr(user, "profile"))
        self.assertTrue(hasattr(user, "farmer_profile"))
        self.assertEqual(user.farmer_profile.farm_name, "farmer's Farm")

    def test_customer_profile_creation(self):
        """Test customer profile creation"""
        user = User.objects.create_user(
            username="customer",
            email="customer@test.com",
            password="TestPass123!",
            phone_number="+8801912345678",
            user_type="customer",
        )

        # Signal should auto-create profiles
        self.assertTrue(hasattr(user, "profile"))
        self.assertTrue(hasattr(user, "customer_profile"))
        self.assertEqual(user.customer_profile.loyalty_points, 0)
