from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='profile')
    username = models.CharField(max_length=100, default="")
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="", blank=True)
    file = models.ImageField(
        upload_to='profile_pictures/', default="", blank=True)
    location = models.CharField(max_length=255, default="", blank=True)
    tel = models.CharField(max_length=20, default="", blank=True)
    type = models.CharField(max_length=20, default="")
    email = models.EmailField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=20, default="")
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    subscription_model = models.CharField(max_length=20, default="")
    is_child = models.BooleanField(default=False)

    def __str__(self):
        return self.username or self.user.username
