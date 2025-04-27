from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from profiles.models import Profile
from rest_framework.authtoken.models import Token
from django.test import TestCase, override_settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from django.conf import settings
from unittest.mock import patch, Mock

from profiles.utils import send_password_reset_email  # Passe den Import-Pfad an


class ProfileAPITests(APITestCase):
    def setUp(self):
        # Erstelle Benutzer
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )
        self.staff_user = User.objects.create_user(
            username="staffuser", email="staffuser@example.com", password="staffpass123", is_staff=True
        )

        # Authentifizierungstoken erstellen
        self.token = Token.objects.create(user=self.user)
        self.staff_token = Token.objects.create(user=self.staff_user)

        # URLs
        self.profile_list_url = reverse('profile-list')
        self.profile_detail_url = reverse('profile-detail', kwargs={'pk': self.user.profile.pk})

    def test_profile_created_with_user(self):
        """Testet, ob ein Profil automatisch mit dem Benutzer erstellt wird."""
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(Profile.objects.first().user, self.user)

    def test_get_profile_list_authenticated(self):
        """Testet das Abrufen der Profil-Liste für authentifizierte Benutzer."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_profile_list_unauthenticated(self):
        """Testet, dass nicht authentifizierte Benutzer keinen Zugriff auf die Profil-Liste haben."""
        response = self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_detail_authenticated(self):
        """Testet das Abrufen eines einzelnen Profils für authentifizierte Benutzer."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.profile.username)

    def test_update_profile_authenticated(self):
        """Testet das Aktualisieren eines Profils für authentifizierte Benutzer."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            "location": "Updated City",
            "tel": "111222333"
        }
        response = self.client.patch(self.profile_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.location, "Updated City")
        self.assertEqual(self.user.profile.tel, "111222333")

    def test_update_profile_unauthorized(self):
        """Testet, dass ein normaler Benutzer ohne Berechtigung ein fremdes Profil nicht aktualisieren kann."""
        # Authentifiziere mit einem normalen Benutzer (kein Staff-User)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            "location": "Unauthorized Update"
        }
        # Versuche, das Profil eines anderen Benutzers zu aktualisieren
        response = self.client.patch(reverse('profile-detail', kwargs={'pk': self.staff_user.profile.pk}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_profile_not_allowed(self):
        """Testet, dass das Löschen eines Profils nicht erlaubt ist."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(self.profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

class SendPasswordResetEmailTests(TestCase):
    def setUp(self):
        """Setup-Methode erstellt einen Testbenutzer für alle Tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPassword123!"
        )
        
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_is_sent(self, mock_settings):
        """Testet, ob eine E-Mail gesendet wird."""
        # Mock die settings.FRONTEND_URL
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        self.assertEqual(len(mail.outbox), 1)
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_recipient(self, mock_settings):
        """Testet, ob die E-Mail an den richtigen Empfänger gesendet wird."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_subject(self, mock_settings):
        """Testet, ob der Betreff der E-Mail korrekt ist."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        self.assertEqual(mail.outbox[0].subject, "Passwort zurücksetzen")
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_content_contains_username(self, mock_settings):
        """Testet, ob der Inhalt der E-Mail den Benutzernamen enthält."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        self.assertIn(self.user.username, mail.outbox[0].body)
        # Prüfe auch den HTML-Inhalt
        self.assertIn(self.user.username, mail.outbox[0].alternatives[0][0])
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_content_contains_reset_url(self, mock_settings):
        """Testet, ob der Inhalt der E-Mail die Zurücksetz-URL enthält."""
        frontend_url = 'http://localhost:4200'
        mock_settings.FRONTEND_URL = frontend_url
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        # Token und UID für die erwartete URL generieren
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        expected_url = f"{frontend_url}/password-reset-confirm/{uid}/{token}"
        
        # Mock für default_token_generator.make_token um konsistente Token-Werte zu haben
        with patch('django.contrib.auth.tokens.default_token_generator.make_token', return_value=token):
            send_password_reset_email(self.user)
            self.assertIn(expected_url, mail.outbox[0].body)
            # Prüfe auch den HTML-Inhalt
            self.assertIn(expected_url, mail.outbox[0].alternatives[0][0])
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_has_html_alternative(self, mock_settings):
        """Testet, ob die E-Mail eine HTML-Alternative enthält."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_html_contains_reset_button(self, mock_settings):
        """Testet, ob der HTML-Inhalt einen Reset-Button enthält."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        html_content = mail.outbox[0].alternatives[0][0]
        self.assertIn("Passwort zurücksetzen", html_content)
        self.assertIn("style=\"background-color: #2E3EDF; color: white;", html_content)
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_contains_logo(self, mock_settings):
        """Testet, ob der HTML-Inhalt einen Verweis auf das Logo enthält."""
        frontend_url = 'http://localhost:4200'
        mock_settings.FRONTEND_URL = frontend_url
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        html_content = mail.outbox[0].alternatives[0][0]
        expected_logo_url = f"{frontend_url}/assets/images/logo.png"
        self.assertIn(expected_logo_url, html_content)
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_contains_validity_message(self, mock_settings):
        """Testet, ob der E-Mail-Inhalt den Hinweis zur Gültigkeit des Links enthält."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        self.assertIn("24 Stunden gültig", mail.outbox[0].body)
        html_content = mail.outbox[0].alternatives[0][0]
        self.assertIn("24 Stunden gültig", html_content)
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('registration.utils.settings')
    def test_email_from_address(self, mock_settings):
        """Testet, ob die Absenderadresse korrekt ist."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        send_password_reset_email(self.user)
        self.assertEqual(mail.outbox[0].from_email, 'test@example.com')
    
    @patch('django.core.mail.EmailMultiAlternatives.send')
    @patch('registration.utils.settings')
    def test_exception_handling(self, mock_settings, mock_send):
        """Testet, ob Ausnahmen beim Senden ordnungsgemäß abgefangen werden."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        # Simuliere einen Fehler beim Senden
        mock_send.side_effect = Exception("Simulated error")
        
        # Die Funktion sollte keine Exception werfen, sondern sie abfangen
        with patch('builtins.print') as mock_print:
            # Die Funktion wird aufgerufen und sollte keine Exception auslösen
            send_password_reset_email(self.user)
            
            # Überprüfe, ob die Fehlermeldung gedruckt wurde
            mock_print.assert_called_with("Error sending password reset email: Simulated error")
    
    @patch('django.core.mail.EmailMultiAlternatives.send')
    @patch('registration.utils.settings')
    def test_successful_send_message(self, mock_settings, mock_send):
        """Testet, ob bei erfolgreichem Senden eine Erfolgsmeldung ausgegeben wird."""
        mock_settings.FRONTEND_URL = 'http://localhost:4200'
        mock_settings.DEFAULT_FROM_EMAIL = 'test@example.com'
        
        with patch('builtins.print') as mock_print:
            send_password_reset_email(self.user)
            
            # Überprüfe, ob die Erfolgsmeldung gedruckt wurde
            mock_print.assert_called_with(f"Password reset email sent successfully to {self.user.email}")
    
