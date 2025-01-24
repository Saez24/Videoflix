from django.db import models
from datetime import date, timedelta

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateField(default=date.today)
    url = models.URLField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)

    def is_new(self):
        return date.today() - self.created_at <= timedelta(days=30)
    
    def is_popular(self):
        return self.views >= 10