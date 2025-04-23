from rest_framework import status
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.authtoken.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from content.models import Video
from .seriallizers import ContentSerializer
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

@method_decorator(csrf_protect, name='dispatch')
class ContentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContentSerializer         
    queryset = Video.objects.all()

    def get(self, request, format=None):
        videos = Video.objects.all()
        serializer = ContentSerializer(videos, many=True)
        return Response(serializer.data)
        
    def post(self, request, *args, **kwargs):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_protect, name='dispatch')
class ContentViewPK(APIView):
    permission_classes = [AllowAny]
    serializer_class = ContentSerializer

    def get(self, request, pk, format=None):
        video = get_object_or_404(Video, pk=pk)
        serializer = ContentSerializer(video)
        return Response(serializer.data)
        
    def put(self, request, pk, format=None):
        video = get_object_or_404(Video, pk=pk)
        serializer = ContentSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        video = get_object_or_404(Video, pk=pk)
        video.delete()  # Löscht das Video und löst das post_delete-Signal aus
        return Response({"message": "Video deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

# class VideoDeleteView(APIView):
#     def delete(self, request, video_id, format=None):
#         video = get_object_or_404(Video, id=video_id)
#         video.delete()  # Löscht das Video und löst das post_delete-Signal aus
#         return Response({"message": "Video deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        