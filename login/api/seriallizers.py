from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            raise serializers.ValidationError(
                {"detail": "Username and Password are required."})
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                {"detail": "Wrong username or password."})
        data['user'] = user
        return data