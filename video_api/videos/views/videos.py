from rest_framework import viewsets, permissions
from videos.serializers import VideoSerializer
from videos.models import Video
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from moviepy.editor import VideoFileClip
import os
from django.conf import settings
import ffmpeg
import uuid


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def trim(self, request, pk=None):
        """ Allows trimming a video by providing start_time and/or end_time. """
        video = self.get_video(pk)
        if not video:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        start_time, end_time = self.get_trim_times(request, video)
        if start_time is None and end_time is None:
            return Response({"error": "Invalid time values provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not self.validate_times(start_time, end_time, video):
            return Response({"error": "Invalid trimming times."}, status=status.HTTP_400_BAD_REQUEST)

        trimmed_video, output_path = self.trim_video(video.file.path, start_time, end_time)

        new_video = Video.objects.create(
            title=f"Trimmed - {video.title}",
            file=output_path
        )
        serializer = self.serializer_class(new_video, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def get_video(self, pk):
        """Fetch the video object from the database."""
        try:
            return Video.objects.get(id=pk)
        except Video.DoesNotExist:
            return None

    def get_trim_times(self, request, video):
        """Extract start_time and end_time from request data."""
        start_time = request.data.get('start_time', 0)
        end_time = request.data.get('end_time', video.duration)
        try:
            start_time = float(start_time)
            end_time = float(end_time)
        except ValueError:
            return None, None
        return start_time, end_time

    def validate_times(self, start_time, end_time, video):
        """Validate that the provided times are valid."""
        if start_time is None or start_time < 0:
            return False
        if end_time is None or end_time <= start_time or end_time > video.duration:
            return False
        return True

    def generate_unique_filename(self, video_path):
        """Generate a unique filename using UUID."""
        unique_id = uuid.uuid4()
        return f"trimmed_{unique_id}_{os.path.basename(video_path)}"

    def ensure_directory_exists(self, directory_path):
        """Ensure the output directory exists."""
        os.makedirs(directory_path, exist_ok=True)

    def calculate_trimmed_video_size(self, video, target_height):
        """Calculate new dimensions for the trimmed video while maintaining the aspect ratio."""
        video_width, video_height = video.size
        aspect_ratio = video_width / video_height
        target_width = int(target_height * aspect_ratio)
        return target_width, target_height

    def resize_video(self, video, target_size):
        """Resize the video to the specified dimensions."""
        return video.resize(newsize=target_size)

    def trim_audio(self, audio, start_time, end_time):
        """Trim the audio to match the start and end times."""
        return audio.subclip(start_time, end_time)

    def trim_video_content(self, video, start_time, end_time):
        """Trim the video content and attach trimmed audio."""
        trimmed_video = video.subclip(start_time, end_time)
        trimmed_audio = self.trim_audio(video.audio, start_time, end_time)
        trimmed_video = trimmed_video.set_audio(trimmed_audio)
        return trimmed_video

    def write_video_to_file(self, trimmed_video, output_path):
        """Write the trimmed video to the specified output file."""
        trimmed_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

    def trim_video(self, video_path, start_time, end_time):
        """Main function to trim the video."""
        video = VideoFileClip(video_path)

        trimmed_video = self.trim_video_content(video, start_time, end_time)

        target_height = video.h
        target_width, target_height = self.calculate_trimmed_video_size(video, target_height)
        trimmed_video = self.resize_video(trimmed_video, target_size=(target_height, target_width))

        output_filename = self.generate_unique_filename(video_path)
        output_path = os.path.join(settings.MEDIA_ROOT, 'trimmed_videos', output_filename)

        self.ensure_directory_exists(os.path.dirname(output_path))
        self.write_video_to_file(trimmed_video, output_path)

        video.close()

        return trimmed_video, output_path
