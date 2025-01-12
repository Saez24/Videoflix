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
    queryset = SubProfile.objects.all()
    serializer_class = SubProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubProfile.objects.filter(parent_profile__user=self.request.user)
