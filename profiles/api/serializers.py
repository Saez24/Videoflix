from rest_framework import serializers
from profiles.models import Profile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    # Verwende den UserSerializer, um das User-Objekt zu serialisieren
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'type',
            'email',
            'created_at',
            'updated_at',
            'uploaded_at',
            'language',
            'is_verified',
            'is_active',
            'subscription_model',
            'is_child',
            'description',
            'working_hours',
        ]
        extra_kwargs = {
            'last_name': {'required': False},
            'file': {'required': False, 'allow_null': True},
            'location': {'required': False},
            'tel': {'required': False},
            'type': {'required': False},
            'email': {'required': False},
            'language': {'required': False},
            'subscription_model': {'required': False},
            'is_child': {'required': False},
        }
