from unicodedata import category
from django.db import models
from datetime import date, timedelta
import os

class Video(models.Model):
    CATEGORY_CHOICES = [
        ('music', 'Music'),
        ('gaming', 'Gaming'),
        ('education', 'Education'),
        ('comedy', 'Comedy'),
        ('sports', 'Sports'),
        ('tech', 'Tech'),
        ('ducumentary', 'Ducumentary'),
        ('drama', 'Drama'),
        ('news', 'News'),
        ('entertainment', 'Entertainment'),
        ('action', 'Action'),
        ('horror', 'Horror'),
        ('romance', 'Romance'),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateField(default=date.today)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='music')
    hls_playlist = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    def is_new(self):
        return date.today() - self.created_at <= timedelta(days=30)
    
    def is_popular(self):
        return self.views >= 10
    
    def delete(self, *args, **kwargs):
        video_path = self.video_file.path if self.video_file and hasattr(self.video_file, 'path') else None
        thumbnail_path = self.thumbnail.path if self.thumbnail and hasattr(self.thumbnail, 'path') else None
        
        hls_dir = None
        if self.hls_playlist and os.path.exists(self.hls_playlist):
            hls_dir = os.path.dirname(self.hls_playlist)
        
        result = super().delete(*args, **kwargs)
        
        if video_path and os.path.isfile(video_path):
            os.remove(video_path)
            print(f"Video file deleted: {video_path}")
            
        if thumbnail_path and os.path.isfile(thumbnail_path):
            os.remove(thumbnail_path)
            print(f"Thumbnail deleted: {thumbnail_path}")
        
        if hls_dir and os.path.isdir(hls_dir):
            import shutil
            shutil.rmtree(hls_dir)
            print(f"HLS directory deleted: {hls_dir}")
            
        return result