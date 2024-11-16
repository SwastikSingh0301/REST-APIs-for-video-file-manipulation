from django.db import models
from django.contrib.auth.models import User  # Import User model
from moviepy.editor import VideoFileClip
import os


class Video(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='videos/')  # Store in "videos/" directory
    size = models.FloatField(blank=True, null=True)  # Size in MB, allow null initially
    duration = models.FloatField(blank=True, null=True)  # Duration in seconds
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,  # Delete video if the user is deleted
    #     related_name='videos'  # Optional, allows reverse access via user.videos
    # )

    # def __str__(self):
    #     return f"{self.title} by {self.user.username}"

    def save(self, *args, **kwargs):
        # Call the parent save method to save the file first
        super().save(*args, **kwargs)

        # Only process if a file exists
        if self.file:
            video_path = self.file.path

            # Calculate file size
            self.size = os.path.getsize(video_path) / (1024 * 1024)  # Convert bytes to MB

            # Calculate duration using moviepy
            try:
                clip = VideoFileClip(video_path)
                self.duration = clip.duration  # Duration in seconds
                clip.close()
            except Exception as e:
                raise ValueError(f"Error processing video: {str(e)}")

            # Save the updated fields
            super().save(update_fields=["size", "duration"])