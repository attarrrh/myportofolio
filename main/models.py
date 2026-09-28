import uuid
from django.db import models
from django.contrib.auth.models import User
import os


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None
class ExperienceMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(
        Experience, related_name="media", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="experience/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def is_image(self):
        return os.path.splitext(self.file.name)[1].lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    @property
    def is_video(self):
        return os.path.splitext(self.file.name)[1].lower() in {".mp4", ".webm", ".mov"}
    
class GalleryItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
    ]
 
    CATEGORY_CHOICES = [
        ('hobby', 'Hobby'),
        ('interest', 'Interest'),
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('other', 'Other'),
    ]
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    caption = models.TextField(blank=True, default="")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='photo')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='hobby')
    media_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(User, related_name="liked_gallery_items", blank=True)
    media_file = models.FileField(upload_to="gallery/")
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return self.title