from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class CustomLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                {"detail": "Email and Password are required."}
            )

        # Verwende das benutzerdefinierte Backend zur Authentifizierung
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                {"detail": "Wrong email or password."}
            )

        data['user'] = user
        return data