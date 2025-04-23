from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from profiles.models import Profile
from registration.api.seriallizers import RegistrationSerializer
from unittest.mock import patch

class RegistrationSerializerTests(APITestCase):
    def setUp(self):
        self.valid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Testpassword123!"
        }
        self.invalid_email_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "Testpassword123!"
        }
        self.duplicate_email_data = {
            "username": "testuser2",
            "email": "testuser@example.com",
            "password": "Testpassword123!"
        }

    def test_registration_successful(self):
        """Testet, ob ein Benutzer erfolgreich registriert wird."""
        serializer = RegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        with patch("registration.api.seriallizers.send_confirmation_email") as mock_send_email:
            user = serializer.save()
            mock_send_email.assert_called_once_with(user)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        user = User.objects.first()
        profile = Profile.objects.first()
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(profile.user, user)

    def test_registration_invalid_email(self):
        """Testet, ob die Registrierung mit einer ungültigen E-Mail fehlschlägt."""
        serializer = RegistrationSerializer(data=self.invalid_email_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_registration_duplicate_email(self):
        """Testet, ob die Registrierung fehlschlägt, wenn die E-Mail bereits existiert."""
        User.objects.create_user(username="existinguser", email="testuser@example.com", password="password123")
        serializer = RegistrationSerializer(data=self.duplicate_email_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_registration_duplicate_username(self):
        """Testet, ob die Registrierung fehlschlägt, wenn der Benutzername bereits existiert."""
        User.objects.create_user(username="testuser", email="another@example.com", password="password123")
        serializer = RegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_password_validation(self):
        """Testet, ob das Passwort validiert wird."""
        invalid_password_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "123"  # Zu kurz
        }
        serializer = RegistrationSerializer(data=invalid_password_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_profile_creation(self):
        """Testet, ob ein Profil automatisch mit dem Benutzer erstellt wird."""
        serializer = RegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        with patch("registration.api.seriallizers.send_confirmation_email"):
            user = serializer.save()

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.username, user.username)
        self.assertEqual(profile.email, user.email)

    def test_confirmation_email_sent(self):
        """Testet, ob die Bestätigungs-E-Mail gesendet wird."""
        serializer = RegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        with patch("registration.api.seriallizers.send_confirmation_email") as mock_send_email:
            user = serializer.save()
            mock_send_email.assert_called_once_with(user)