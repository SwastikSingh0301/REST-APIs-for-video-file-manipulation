from django.db import models
from django.contrib.auth.models import User  # Import User model


class Video(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='videos/')  # Store in "videos/" directory
    size = models.FloatField()  # Size in MB
    duration = models.FloatField()  # Duration in seconds
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Delete video if the user is deleted
        related_name='videos'  # Optional, allows reverse access via user.videos
    )

    def __str__(self):
        return f"{self.title} by {self.user.username}"