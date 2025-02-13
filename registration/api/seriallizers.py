from django.contrib.auth.models import User
from rest_framework import serializers
from profiles.models import Profile
from django.contrib.auth.password_validation import validate_password
from registration.utils import send_confirmation_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']


class ProfileSerializer(serializers.ModelSerializer):
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
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
        extra_kwargs = {
            'last_name': {'required': False},
            'file': {'required': False, 'allow_null': True},
            'location': {'required': False},
            'tel': {'required': False},
            'description': {'required': False},
            'working_hours': {'required': False},
        }


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese E-Mail ist bereits registriert.")
        return value    

    def save(self):
        pw = self.validated_data['password']
        

        # # Überprüfe, ob die E-Mail bereits vergeben ist
        # if User.objects.filter(email=self.validated_data['email']).exists():
        #     raise serializers.ValidationError(
        #         {"email": ["This email is already in use."]},
        #     )

        # Überprüfe, ob der Benutzername bereits vergeben ist
        if User.objects.filter(username=self.validated_data['username']).exists():
            raise serializers.ValidationError(
                {"username": ["This username is already in use."]},
            )

        # Erstelle den Benutzer
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            is_active=False
        )
        account.set_password(pw)
        account.save()

        # Erstelle das Profil, wenn noch keines existiert
        profile, created = Profile.objects.get_or_create(
            user=account,
            defaults={
                'username': account.username,
                'first_name': account.first_name,
                'last_name': account.last_name,
                'email': account.email,

            }
        )

        # Aktualisiere das Profil, falls es bereits existiert
        profile.username = account.username
        profile.first_name = account.first_name
        profile.last_name = account.last_name
        profile.email = account.email

        profile.save()
        
        send_confirmation_email(account)

        return account