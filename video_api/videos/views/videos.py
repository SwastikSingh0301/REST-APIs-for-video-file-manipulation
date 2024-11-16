from rest_framework import viewsets, permissions
from videos.serializers import VideoSerializer
from videos.models import Video
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from moviepy.editor import VideoFileClip
import os
from django.conf import settings


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
