from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, DateTimeInput

from main.models import Experience, GalleryItem


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]

        labels = {
            "title": "Judul Pengalaman",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "URL Thumbnail",
            "ended_at": "Tanggal Selesai (kosongkan jika masih berjalan)",
        }

        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Software Engineer Intern", "maxlength": 255}
            ),
            "description": Textarea(
                attrs={"placeholder": "Ceritakan pengalamanmu", "rows": 3}
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}
            ),
            "started_at": DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "ended_at": DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }


class GalleryItemForm(ModelForm):
    class Meta:
        model = GalleryItem
        fields = [
            "title",
            "caption",
            "media_type",
            "category",
            "media_url",
        ]

        labels = {
            "title": "Judul",
            "caption": "Caption",
            "media_type": "Tipe Media",
            "category": "Kategori",
            "media_url": "URL Media",
        }

        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Liburan ke Bali", "maxlength": 255}
            ),
            "caption": Textarea(
                attrs={"placeholder": "Ceritakan momen ini", "rows": 3}
            ),
            "media_type": Select(),
            "category": Select(),
            "media_url": URLInput(
                attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}
            ),
        }