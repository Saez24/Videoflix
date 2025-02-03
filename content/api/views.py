from rest_framework.views import APIView
from rest_framework.response import Response
from profiles.models import Profile
from content.models import Video
from .seriallizers import ContentSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny

import logging

logger = logging.getLogger(__name__)

class ContentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:         
            videos = Video.objects.all()
            serializer = ContentSerializer(videos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({
                "detail": "Profile not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({
                "detail": str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)  # Log the error
            return Response({
                "detail": "An error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)