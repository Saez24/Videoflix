from rest_framework import serializers
from content.models import Video


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'