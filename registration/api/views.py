from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .seriallizers import RegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from profiles.models import Profile
from rest_framework import status
from django.contrib.auth.models import User


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request.data['username'] = generate_username(request)
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            generate_profile(request, saved_account)

            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.pk,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_username(request):
    email = request.data.get('email', '')
    username = email.split('@')[0]  # Nutze den Teil vor dem @ als Benutzernamen
    username = username.replace('.', '_').lower()  # Ersetze Punkte durch Unterstriche

    # Stelle sicher, dass der Benutzername eindeutig ist
    counter = 1
    original_username = username
    while User.objects.filter(username=username).exists():
        username = f"{original_username}_{counter}"
        counter += 1

    return username


def generate_profile(request, saved_account):
    profile_type = request.data.get('type', 'customer')

    first_name_registration = request.data.get('first_name', '')
    last_name_registration = request.data.get('last_name', '')

    # Aktualisiere den Benutzer mit den zusätzlichen Daten
    saved_account.first_name = first_name_registration
    saved_account.last_name = last_name_registration
    saved_account.save()

    # Erstelle oder aktualisiere das Profil
    profile, created = Profile.objects.get_or_create(
        user=saved_account,
        defaults={
            'username': saved_account.username,
            'first_name': first_name_registration,
            'last_name': last_name_registration,
            'email': saved_account.email,
            'type': profile_type,
        }
    )

    if not created:
        profile.username = saved_account.username
        profile.first_name = first_name_registration
        profile.last_name = last_name_registration
        profile.email = saved_account.email
        profile.type = profile_type
        profile.save()