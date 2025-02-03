from rest_framework import serializers
from sub_profiles.models import SubProfile
from django.contrib.auth.models import User
from profiles.api.serializers import ProfileSerializer
from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['pk', 'username', 'first_name', 'last_name', 'email']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name', 'email']        


class SubProfileSerializer(serializers.ModelSerializer):
    parent_profile = ProfileSerializer()
    file = serializers.ImageField(use_url=True)

    class Meta:
        model = SubProfile
        fields = [
            'parent_profile',  # Beziehung zum Hauptprofil
            'username',
            'first_name',
            'last_name',
            'file',
            'created_at',
            'updated_at',
            'is_child',
        ]
        extra_kwargs = {
            'last_name': {'required': False},
            'file': {'required': False, 'allow_null': True},
            'is_child': {'required': False},
        }
