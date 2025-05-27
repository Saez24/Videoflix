from rest_framework import serializers
from profiles.models import Profile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name','is_active', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()


    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'file',
            'location',
            'tel',
            'email',
            'created_at',
            'updated_at',
            'uploaded_at',
            'language',
        ]
