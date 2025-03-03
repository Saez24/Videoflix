from unicodedata import category
from django.db import models
from datetime import date, timedelta

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
        # Weitere Kategorien hier hinzufügen
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