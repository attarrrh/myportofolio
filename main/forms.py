from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, DateTimeInput, ClearableFileInput, FileField
from django.core.exceptions import ValidationError
from main.models import Experience, GalleryItem
import os


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]


class ExperienceForm(ModelForm):
    ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm", ".mov", ".pdf"}
    MAX_SIZE = 25 * 1024 * 1024  # 25 MB per file

    media_files = MultipleFileField(
        required=False,
        label="File (foto / video / PDF, boleh pilih lebih dari satu)",
        widget=MultipleFileInput(attrs={"accept": "image/*,video/*,application/pdf"}),
    )

    class Meta:
        model = Experience
        fields = ["title", "description", "category", "ended_at"]

        labels = {
            "title": "Judul Pengalaman",
            "description": "Deskripsi",
            "category": "Kategori",
            "ended_at": "Tanggal Selesai (kosongkan jika masih berjalan)",
        }

        widgets = {
            "title": TextInput(attrs={"placeholder": "Software Engineer Intern", "maxlength": 255}),
            "description": Textarea(attrs={"placeholder": "Ceritakan pengalamanmu", "rows": 3}),
            "category": Select(),
            "ended_at": DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def clean_media_files(self):
        files = [f for f in self.cleaned_data.get("media_files", []) if f]
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in self.ALLOWED_EXT:
                raise ValidationError(f"Format file tidak didukung: {f.name}")
            if f.size > self.MAX_SIZE:
                raise ValidationError(f"{f.name} lebih dari 25 MB.")
        return files

class GalleryItemForm(ModelForm):
    PHOTO_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    VIDEO_EXT = {".mp4", ".webm", ".mov"}
    MAX_SIZE = 25 * 1024 * 1024  # 25 MB

    class Meta:
        model = GalleryItem
        fields = ["title", "caption", "media_type", "category", "media_file"]

        labels = {
            "title": "Judul",
            "caption": "Caption",
            "media_type": "Tipe Media",
            "category": "Kategori",
            "media_file": "File Foto / Video",
        }

        widgets = {
            "title": TextInput(attrs={"placeholder": "Liburan ke Bali", "maxlength": 255}),
            "caption": Textarea(attrs={"placeholder": "Ceritakan momen ini", "rows": 3}),
            "media_type": Select(),
            "category": Select(),
            "media_file": ClearableFileInput(attrs={"accept": "image/*,video/*"}),
        }

    def clean(self):
        cleaned = super().clean()
        f = cleaned.get("media_file")
        media_type = cleaned.get("media_type")

        # hanya cek kalau user memang upload file baru
        if f and hasattr(f, "content_type"):
            ext = os.path.splitext(f.name)[1].lower()
            allowed = self.PHOTO_EXT if media_type == "photo" else self.VIDEO_EXT
            if ext not in allowed:
                self.add_error(
                    "media_file",
                    f"Format tidak cocok dengan tipe media. Boleh: {', '.join(sorted(allowed))}",
                )
            if f.size > self.MAX_SIZE:
                self.add_error("media_file", "Ukuran file maksimal 25 MB.")
        return cleaned