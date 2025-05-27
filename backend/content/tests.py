import subprocess
from rest_framework.test import APITestCase
from rest_framework import status
from content.models import Video
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import os
import unittest
from unittest import mock
from django.test import TestCase
from django.conf import settings

from content.tasks import (
    exportJson, 
    create_base_directory, 
    create_master_playlist, 
    generate_ffmpeg_command, 
    convert_to_hls,
    delete_mp4,
    QUALITIES
)

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

class ExportJsonTests(TestCase):
    
    @mock.patch('content.tasks.subprocess.run')
    def test_export_json(self, mock_run):
        """Test that exportJson calls subprocess.run with correct command"""
        exportJson()
        mock_run.assert_called_once()
        # Überprüfe, dass der Aufruf 'shell=True' enthält
        self.assertTrue(mock_run.call_args[1]['shell'])
        # Überprüfe, dass der Aufruf den python3 manage.py shell Befehl enthält
        self.assertIn('python3 manage.py shell', mock_run.call_args[0][0])


class CreateBaseDirectoryTests(TestCase):
    
    @mock.patch('content.tasks.os.makedirs')
    def test_create_base_directory(self, mock_makedirs):
        """Test that create_base_directory creates the directory correctly"""
        source = '/path/to/video.mp4'
        result = create_base_directory(source)
        
        expected_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', 'video')
        mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)
        self.assertEqual(result, expected_path)


class CreateMasterPlaylistTests(TestCase):
    
    @mock.patch('content.tasks.open', new_callable=mock.mock_open)
    def test_create_master_playlist(self, mock_file):
        """Test that create_master_playlist creates the correct m3u8 file"""
        base_name = '/media/videos/hls/video'
        qualities = {'720p': ('1280x720', '2800k')}
        
        result = create_master_playlist(base_name, qualities)
        
        # Überprüfe, dass die Datei geöffnet wurde
        mock_file.assert_called_once_with(os.path.join(base_name, 'playlist.m3u8'), 'w')
        
        # Überprüfe den Inhalt der Datei
        handle = mock_file()
        expected_calls = [
            mock.call("#EXTM3U\n"),
            mock.call("#EXT-X-VERSION:3\n"),
            mock.call("#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720\n"),
            mock.call("720p.m3u8\n")
        ]
        handle.write.assert_has_calls(expected_calls)
        
        # Überprüfe den zurückgegebenen Pfad
        self.assertEqual(result, os.path.relpath(os.path.join(base_name, 'playlist.m3u8'), settings.MEDIA_ROOT))


class GenerateFfmpegCommandTests(TestCase):
    
    def test_generate_ffmpeg_command(self):
        """Test that generate_ffmpeg_command returns the correct command"""
        source = '/path/to/video.mp4'
        base_name = '/media/videos/hls/video'
        quality = '720p'
        resolution = '1280x720'
        bitrate = '2800k'
        
        result = generate_ffmpeg_command(source, base_name, quality, resolution, bitrate)
        
        expected_cmd = [
            '/usr/bin/ffmpeg',
            '-i', source,
            '-preset', 'fast',
            '-g', '48',
            '-sc_threshold', '0',
            '-map', '0:v',
            '-map', '0:a?',
            '-s:v', resolution,
            '-c:v', 'libx264',
            '-b:v', bitrate,
            '-c:a', 'aac',
            '-strict', '-2',
            '-f', 'hls',
            '-hls_time', '5',
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', f'{base_name}/{quality}_%03d.ts',
            f'{base_name}/{quality}.m3u8'
        ]
        
        self.assertEqual(result, expected_cmd)


class ConvertToHlsTests(TestCase):
    
    def setUp(self):
        # Video-Objekt erstellen
        self.video = Video.objects.create(
            title="Test Video",
            description="Description for Test Video",
            likes=0,
            dislikes=0,
            views=0,
            video_file=SimpleUploadedFile("test.mp4", b"file_content", content_type="video/mp4")
        )
        self.source = os.path.join(settings.MEDIA_ROOT, 'test.mp4')
        self.base_name = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls', 'test')
    
    @mock.patch('content.tasks.delete_mp4')
    @mock.patch('content.tasks.create_master_playlist')
    @mock.patch('content.tasks.subprocess.run')
    @mock.patch('content.tasks.create_base_directory')
    def test_convert_to_hls_success(self, mock_create_base_dir, mock_run, mock_create_master, mock_delete_mp4):
        """Test the full conversion process"""
        # Mocks konfigurieren
        mock_create_base_dir.return_value = self.base_name
        mock_run.return_value = mock.Mock(stdout="", stderr="")
        mock_create_master.return_value = 'videos/hls/test/playlist.m3u8'
        
        # Funktion aufrufen
        convert_to_hls(self.source, self.video.id)
        
        # Überprüfen der Aufrufe
        mock_create_base_dir.assert_called_once_with(self.source)
        
        # Überprüfen, dass subprocess.run für jede Qualität aufgerufen wurde
        self.assertEqual(mock_run.call_count, len(QUALITIES))
        
        # Überprüfen, dass create_master_playlist aufgerufen wurde
        mock_create_master.assert_called_once_with(self.base_name, QUALITIES)
        
        # Überprüfen, dass delete_mp4 aufgerufen wurde
        mock_delete_mp4.assert_called_once_with(self.source)
        
        # Überprüfen, dass die Video-Instanz aktualisiert wurde
        self.video.refresh_from_db()
        expected_path = '/media/videos/hls/test/playlist.m3u8'
        self.assertEqual(self.video.hls_playlist, expected_path)
    
    @mock.patch('content.tasks.subprocess.run')
    @mock.patch('content.tasks.create_base_directory')
    def test_convert_to_hls_subprocess_error(self, mock_create_base_dir, mock_run):
        """Test error handling when subprocess fails"""
        # Mocks konfigurieren
        mock_create_base_dir.return_value = self.base_name
        mock_run.side_effect = subprocess.CalledProcessError(1, cmd='ffmpeg', stderr="Error message")
        
        # Überprüfen, dass eine Exception ausgelöst wird
        with self.assertRaises(subprocess.CalledProcessError):
            convert_to_hls(self.source, self.video.id)


class DeleteMP4Tests(TestCase):
    
    @mock.patch('content.tasks.os.path.exists')
    @mock.patch('content.tasks.os.remove')
    def test_delete_mp4_file_exists(self, mock_remove, mock_exists):
        """Test that delete_mp4 removes the file when it exists"""
        source = '/path/to/video.mp4'
        mock_exists.return_value = True
        
        delete_mp4(source)
        
        mock_exists.assert_called_once_with(source)
        mock_remove.assert_called_once_with(source)
    
    @mock.patch('content.tasks.os.path.exists')
    @mock.patch('content.tasks.os.remove')
    def test_delete_mp4_file_not_exists(self, mock_remove, mock_exists):
        """Test that delete_mp4 doesn't try to remove the file when it doesn't exist"""
        source = '/path/to/video.mp4'
        mock_exists.return_value = False
        
        delete_mp4(source)
        
        mock_exists.assert_called_once_with(source)
        mock_remove.assert_not_called()        