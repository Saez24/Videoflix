from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from profiles.models import Profile
from rest_framework.authtoken.models import Token

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