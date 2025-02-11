from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='profile')
    username = models.CharField(max_length=100, default="")
    file = models.ImageField(
        upload_to='profile_pictures/', default="", blank=True)
    location = models.CharField(max_length=255, default="", blank=True)
    tel = models.CharField(max_length=20, default="", blank=True)
    email = models.EmailField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=20, default="")

    def __str__(self):
        return self.username or self.user.username
