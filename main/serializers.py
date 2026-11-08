from django.db import transaction
from django.template.defaultfilters import date as date_filter
from django.utils.html import strip_tags
from rest_framework import serializers

from main.forms import ExperienceForm, GalleryItemForm, sanitize_html_text
from main.models import Experience, ExperienceMedia, GalleryItem, Project


class CleanTextSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        value = strip_tags(sanitize_html_text(value)).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value


class StarFieldsMixin:
    star_relation = "starred_by"

    def get_star_count(self, obj):
        return getattr(obj, self.star_relation).count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and any(
            user.pk == request.user.pk for user in getattr(obj, self.star_relation).all()
        ))

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in getattr(obj, self.star_relation).all())


class ProjectSerializer(StarFieldsMixin, CleanTextSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "title", "description", "tech_stack", "project_url",
                  "project_image_url", "star_count", "is_starred", "starred_by_names"]
        read_only_fields = ["id"]

    def validate_description(self, value):
        return strip_tags(sanitize_html_text(value)).strip()

    def validate_tech_stack(self, value):
        return strip_tags(sanitize_html_text(value)).strip()


class GalleryItemSerializer(StarFieldsMixin, CleanTextSerializer):
    star_relation = "liked_by"
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    media_url = serializers.URLField(required=False, allow_blank=True)
    media_file = serializers.FileField(required=False, write_only=True)
    display_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryItem
        fields = ["id", "title", "caption", "media_type", "category", "category_display",
                  "media_url", "media_file", "display_url", "created_at", "star_count",
                  "is_starred", "starred_by_names"]
        read_only_fields = ["id", "created_at"]

    def get_display_url(self, obj):
        if not obj.media_file:
            return obj.media_url
        request = self.context.get("request")
        return request.build_absolute_uri(obj.media_file.url) if request else obj.media_file.url

    def validate_caption(self, value):
        return strip_tags(sanitize_html_text(value)).strip()

    def validate(self, attrs):
        file = attrs.get("media_file")
        existing_file = getattr(self.instance, "media_file", None)
        url = attrs.get("media_url", getattr(self.instance, "media_url", ""))
        if not (file or existing_file or url):
            raise serializers.ValidationError({"media_file": "Upload a file or provide a media URL."})
        if file:
            from pathlib import Path
            kind = attrs.get("media_type", getattr(self.instance, "media_type", "photo"))
            allowed = GalleryItemForm.PHOTO_EXT if kind == "photo" else GalleryItemForm.VIDEO_EXT
            if Path(file.name).suffix.lower() not in allowed:
                raise serializers.ValidationError({"media_file": "File type does not match the selected media type."})
            if file.size > GalleryItemForm.MAX_SIZE:
                raise serializers.ValidationError({"media_file": "File exceeds 25 MB."})
        return attrs


class ExperienceMediaSerializer(serializers.ModelSerializer):
    url = serializers.FileField(source="file", read_only=True)
    filename = serializers.CharField(read_only=True)
    is_image = serializers.BooleanField(read_only=True)
    is_video = serializers.BooleanField(read_only=True)

    class Meta:
        model = ExperienceMedia
        fields = ["id", "url", "filename", "is_image", "is_video"]


class OptionalDateTimeField(serializers.DateTimeField):
    """An empty datetime-local input in multipart means no date, just like ModelForm."""

    def to_internal_value(self, value):
        return None if value == "" else super().to_internal_value(value)


class ExperienceSerializer(CleanTextSerializer):
    ended_at = OptionalDateTimeField(required=False, allow_null=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    started = serializers.SerializerMethodField()
    ended = serializers.SerializerMethodField()
    media = ExperienceMediaSerializer(many=True, read_only=True)
    media_files = serializers.ListField(child=serializers.FileField(), required=False, write_only=True)

    class Meta:
        model = Experience
        fields = ["id", "title", "description", "category", "category_display", "thumbnail",
                  "started_at", "ended_at", "started", "ended", "is_ongoing", "media", "media_files"]
        read_only_fields = ["id"]

    def validate_description(self, value):
        value = strip_tags(sanitize_html_text(value)).strip()
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        return value

    def get_started(self, obj):
        return date_filter(obj.started_at, "M Y") if obj.started_at else ""

    def get_ended(self, obj):
        return "Present" if obj.is_ongoing else date_filter(obj.ended_at, "M Y")

    def validate_media_files(self, files):
        from pathlib import Path
        for file in files:
            if Path(file.name).suffix.lower() not in ExperienceForm.ALLOWED_EXT:
                raise serializers.ValidationError("Unsupported file type.")
            if file.size > ExperienceForm.MAX_SIZE:
                raise serializers.ValidationError("Each file must be at most 25 MB.")
        return files

    @transaction.atomic
    def create(self, validated_data):
        files = validated_data.pop("media_files", [])
        instance = super().create(validated_data)
        for file in files:
            ExperienceMedia.objects.create(experience=instance, file=file)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        files = validated_data.pop("media_files", [])
        instance = super().update(instance, validated_data)
        for file in files:
            ExperienceMedia.objects.create(experience=instance, file=file)
        return instance
