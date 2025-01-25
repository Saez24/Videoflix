from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .seriallizers import RegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from profiles.models import Profile
from rest_framework import status


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request.data['username'] = generate_username(request)
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                "user_id": saved_account.pk
            }
            generate_profile(request, saved_account)
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_username(request):
    username = request.data.get('username', '')
    if ' ' in username:
        username = username.replace(' ', '_')
    return username.lower()


def generate_profile(request, saved_account):
    profile_type = request.data.get('type', 'customer')

    first_name_registration = request.data.get('first_name', '')
    last_name_registration = request.data.get('last_name', '')

    if not first_name_registration or not last_name_registration:
        first_name_registration = ''
        last_name_registration = ''

    user = saved_account
    user.first_name = first_name_registration
    user.last_name = last_name_registration
    user.save()

    # Überprüfe, ob bereits ein Profil existiert
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