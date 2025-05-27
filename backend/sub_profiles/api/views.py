from rest_framework.views import APIView
from rest_framework.response import Response
from sub_profiles.models import SubProfile
from profiles.models import Profile
from .serializers import SubProfileSerializer, UserSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .permissions import IsOwnerOrAdmin
from rest_framework.authentication import TokenAuthentication


class SubProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        # Nur SubProfiles zurückgeben, die zum angemeldeten Benutzer gehören
        sub_profiles = SubProfile.objects.filter(parent_profile__user=request.user)
        serializer = SubProfileSerializer(sub_profiles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubProfileListCreateView(generics.ListCreateAPIView):
    queryset = SubProfile.objects.all()
    serializer_class = SubProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Gibt nur SubProfiles für den authentifizierten Benutzer zurück
        return SubProfile.objects.filter(parent_profile__user=self.request.user)

    def perform_create(self, serializer):
        # Verknüpft das SubProfile automatisch mit dem Hauptprofil des Benutzers
        parent_profile = Profile.objects.get(user=self.request.user)
        serializer.save(parent_profile=parent_profile)


class SubProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubProfile.objects.filter(parent_profile__user=self.request.user)

