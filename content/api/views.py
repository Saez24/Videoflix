from rest_framework.views import APIView
from rest_framework.response import Response
from profiles.models import Profile
from content.models import Video
from .seriallizers import ContentSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated


class ContentViewSets(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=self.request.user)
            if not profile.is_staff:
                raise PermissionDenied("Not allowed to view this content.")
            videos = Video.objects.all()
            serializer = ContentSerializer(videos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound:
            return Response({
                "detail": "Content not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({
                "detail": "Not allowed to view this content."
            }, status=status.HTTP_403_FORBIDDEN)