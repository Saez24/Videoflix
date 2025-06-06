from rest_framework.views import APIView
from rest_framework.response import Response
from profiles.models import Profile
from .serializers import ProfileSerializer, UserSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .permissions import IsOwnerOrAdmin
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from profiles.utils import send_password_reset_email


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff



DEFAULT_TIMEOUT = getattr(settings, 'DEFAULT_TIMEOUT', 60)
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class ProfileListView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = 'pk'

class ProfileViewSets(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @cache_page(CACHE_TTL)
    def get_object(self):
        try:
            pk = self.kwargs.get('pk')
            profile = Profile.objects.get(pk=pk)
            return profile
        except Profile.DoesNotExist:
            raise NotFound("Profile not found")

    def patch(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        except PermissionDenied:
            return Response({
                "detail": "Not allowed to edit this profile."
            }, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        

    def update_profile(self, profile, data):
        profile_serializer = ProfileSerializer(
            profile, data=data, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        return profile_serializer.data

    def update_user(self, user, data):
        user_data = {}
        if 'first_name' in data:
            user_data['first_name'] = data['first_name']
        if 'last_name' in data:
            user_data['last_name'] = data['last_name']
        if 'email' in data:
            user_data['email'] = data['email']

        if user_data:
            user_serializer = UserSerializer(
                user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            return user_serializer.data
        return {}


class ProfileAdultViewSets(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        customer_profiles = Profile.objects.filter(type="customer")
        return_data_customer_profiles = []
        for profile in customer_profiles:
            return_data_customer_profiles.append({
                # Verwende UserSerializer
                "user": UserSerializer(profile.user).data,
                "file": profile.file.url if profile.file else None,
                "location": profile.location,
                "tel": profile.tel,
                "type": profile.type
            })
        return Response(return_data_customer_profiles, status=status.HTTP_200_OK)


class ProfileChildViewSets(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business_profiles = Profile.objects.filter(type="business")
        return_data_business_profiles = []
        for profile in business_profiles:
            return_data_business_profiles.append({
                # Verwende UserSerializer
                "user": UserSerializer(profile.user).data,
                "file": profile.file.url if profile.file else None,
                "location": profile.location,
                "type": profile.type
            })
        return Response(return_data_business_profiles, status=status.HTTP_200_OK)
    

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user)
            return Response(
                {'success': 'Password reset link has been sent to your email'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'No user with this email address'},
                status=status.HTTP_404_NOT_FOUND
            )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if not default_token_generator.check_token(user, token):
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_password = request.data.get('password')
            if not new_password:
                return Response(
                    {'error': 'Password is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(new_password)
            user.save()
            
            # Optional: Update profile if needed
            if hasattr(user, 'profile'):
                user.profile.save()
            
            return Response(
                {'success': 'Password has been reset successfully'},
                status=status.HTTP_200_OK
            )
            
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )