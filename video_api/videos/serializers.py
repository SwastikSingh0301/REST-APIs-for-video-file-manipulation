from rest_framework import serializers
from .models import Video
import moviepy.editor as mp
from rest_framework import serializers
from moviepy.editor import VideoFileClip
from django.core.exceptions import ValidationError
import os

# Define the allowed limits
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
MIN_FILE_SIZE = 5 * 1024 * 1024  # 25 MB
MIN_DURATION = 2  # 5 seconds
MAX_DURATION = 25  # 25 seconds


class VideoSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField(read_only=True)  # Display the username
    size = serializers.FloatField(read_only=True)
    duration = serializers.FloatField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)


    class Meta:
        model = Video
        fields = ['id', 'title', 'file', 'size', 'duration', 'uploaded_at']

    def create(self, validated_data):
        return super().create(validated_data)

    def validate_video_size(self, file):
        """Validate the file size to be less than the max size."""
        if file.size > MAX_FILE_SIZE:
            raise ValidationError(f"File size must be less than {MAX_FILE_SIZE // (1024 * 1024)} MB.")

        if file.size < MIN_FILE_SIZE:
            raise ValidationError(f"File size must be greater than {MIN_FILE_SIZE // (1024 * 1024)} MB.")

    def validate_video_duration(self, file):
        """Validate the video duration to be within the min and max limits."""
        try:
            clip = VideoFileClip(file.temporary_file_path())  # Get the file path for processing
            duration = clip.duration
            clip.close()
        except Exception as e:
            raise ValidationError(f"Error reading video file: {str(e)}")

        if duration > MAX_DURATION:
            raise ValidationError(f"Video duration must be less than {MAX_DURATION} seconds.")
        if duration < MIN_DURATION:
            raise ValidationError(f"Video duration must be greater than {MIN_DURATION} seconds.")

    def validate_file(self, value):
        # video size validation
        self.validate_video_size(value)
        # video duration validation
        self.validate_video_duration(value)
        return value
