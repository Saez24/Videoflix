from django.db import models
from profiles.models import Profile


class SubProfile(models.Model):
    parent_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='subprofiles'
    )
    username = models.CharField(max_length=100, default="")
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="", blank=True)
    file = models.ImageField(
        upload_to='subprofile_pictures/', default="", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_child = models.BooleanField(default=False)

    def __str__(self):
        return self.username
