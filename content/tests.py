from rest_framework.test import APITestCase
from rest_framework import status
from content.models import Video
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class ContentViewTests(APITestCase):
    def setUp(self):
        # Benutzer und Token erstellen
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Dummy-Datei für das video_file Feld
        self.dummy_file = SimpleUploadedFile("dummy.mp4", b"file_content", content_type="video/mp4")

        # Erstelle Testdaten
        self.video1 = Video.objects.create(
            title="Test Video 1",
            description="Description for Test Video 1",
            likes=10,
            dislikes=2,
            views=100,
            video_file=self.dummy_file
        )
        self.video2 = Video.objects.create(
            title="Test Video 2",
            description="Description for Test Video 2",
            likes=5,
            dislikes=1,
            views=50,
            video_file=self.dummy_file
        )
        self.list_url = reverse('video_list')
        self.detail_url = reverse('video_detail', kwargs={'pk': self.video1.pk})

    def test_get_video_list(self):
        """Testet das Abrufen der Liste aller Videos."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_video_detail(self):
        """Testet das Abrufen eines einzelnen Videos."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.video1.title)

    def test_create_video(self):
        """Testet das Erstellen eines neuen Videos."""
        data = {
            "title": "New Video",
            "description": "Description for New Video",
            "likes": 0,
            "dislikes": 0,
            "views": 0,
            "video_file": SimpleUploadedFile("new_dummy.mp4", b"file_content", content_type="video/mp4")
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.count(), 3)

    def test_update_video(self):
        """Testet das Aktualisieren eines Videos."""
        data = {
            "title": "Updated Video",
            "description": "Updated Description",
            "likes": 20,
            "dislikes": 3,
            "views": 200,
            "video_file": SimpleUploadedFile("updated_dummy.mp4", b"file_content", content_type="video/mp4")
        }
        response = self.client.put(self.detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.video1.refresh_from_db()
        self.assertEqual(self.video1.title, "Updated Video")

    def test_delete_video(self):
        """Testet das Löschen eines Videos."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Video.objects.count(), 1)