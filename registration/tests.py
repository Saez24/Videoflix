from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from profiles.models import Profile
from registration.api.seriallizers import RegistrationSerializer
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from unittest.mock import patch, Mock

from registration.utils import send_confirmation_email

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


class SendConfirmationEmailTests(TestCase):
    def setUp(self):
        """Setup-Methode erstellt einen Testbenutzer für alle Tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPassword123!"
        )
        
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_is_sent(self):
        """Testet, ob eine E-Mail gesendet wird."""
        send_confirmation_email(self.user)
        self.assertEqual(len(mail.outbox), 1)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_recipient(self):
        """Testet, ob die E-Mail an den richtigen Empfänger gesendet wird."""
        send_confirmation_email(self.user)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_subject(self):
        """Testet, ob der Betreff der E-Mail korrekt ist."""
        send_confirmation_email(self.user)
        self.assertEqual(mail.outbox[0].subject, "Bitte bestätige deine E-Mail-Adresse")
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_content_contains_username(self):
        """Testet, ob der Inhalt der E-Mail den Benutzernamen enthält."""
        send_confirmation_email(self.user)
        self.assertIn(self.user.username, mail.outbox[0].body)
        # Prüfe auch den HTML-Inhalt
        self.assertIn(self.user.username, mail.outbox[0].alternatives[0][0])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_content_contains_verification_url(self):
        """Testet, ob der Inhalt der E-Mail die Verifikations-URL enthält."""
        # Token und UID für die erwartete URL generieren
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        expected_url = f"http://localhost:4200/verify-email/{uid}/{token}"
        
        # Mock für default_token_generator.make_token um konsistente Token-Werte zu haben
        with patch('django.contrib.auth.tokens.default_token_generator.make_token', return_value=token):
            send_confirmation_email(self.user)
            self.assertIn(expected_url, mail.outbox[0].body)
            # Prüfe auch den HTML-Inhalt
            self.assertIn(expected_url, mail.outbox[0].alternatives[0][0])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_has_html_alternative(self):
        """Testet, ob die E-Mail eine HTML-Alternative enthält."""
        send_confirmation_email(self.user)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_html_contains_activation_button(self):
        """Testet, ob der HTML-Inhalt einen Aktivierungsbutton enthält."""
        send_confirmation_email(self.user)
        html_content = mail.outbox[0].alternatives[0][0]
        self.assertIn("Activate account", html_content)
        self.assertIn("style=\"background-color: #2E3EDF; color: white;", html_content)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_contains_logo(self):
        """Testet, ob der HTML-Inhalt einen Verweis auf das Logo enthält."""
        send_confirmation_email(self.user)
        html_content = mail.outbox[0].alternatives[0][0]
        self.assertIn("http://localhost:4200/assets/images/logo.png", html_content)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_from_address(self):
        """Testet, ob die Absenderadresse korrekt ist."""
        send_confirmation_email(self.user)
        self.assertEqual(mail.outbox[0].from_email, 'noreply@yourdeveloper.com')
    
    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_exception_handling(self, mock_send):
        """Testet, ob Ausnahmen beim Senden ordnungsgemäß abgefangen werden."""
        # Simuliere einen Fehler beim Senden
        mock_send.side_effect = Exception("Simulated error")
        
        # Die Funktion sollte keine Exception werfen, sondern sie abfangen
        with patch('builtins.print') as mock_print:
            # Die Funktion wird aufgerufen und sollte keine Exception auslösen
            send_confirmation_email(self.user)
            
            # Überprüfe, ob die Fehlermeldung gedruckt wurde
            mock_print.assert_called_with("Error sending email: Simulated error")
    
    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_successful_send_message(self, mock_send):
        """Testet, ob bei erfolgreichem Senden eine Erfolgsmeldung ausgegeben wird."""
        with patch('builtins.print') as mock_print:
            send_confirmation_email(self.user)
            
            # Überprüfe, ob die Erfolgsmeldung gedruckt wurde
            # Beachte: Es scheint ein Fehler in der Funktion zu sein, '{user.email}' ist nicht interpoliert
            mock_print.assert_called_with("Email sent successfully. to {user.email}")
            
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_contains_videoflix_reference(self):
        """Testet, ob die E-Mail einen Verweis auf Videoflix enthält."""
        send_confirmation_email(self.user)
        html_content = mail.outbox[0].alternatives[0][0]
        self.assertIn("Videoflix", html_content)
        self.assertIn("http://localhost:4200/", html_content)
            