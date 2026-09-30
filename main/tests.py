from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
import tempfile

from main.forms import ExperienceForm
from main.models import Experience, GalleryItem


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        user = self.client.login(username="admin", password="admin123")
        if not user:
            from django.contrib.auth import get_user_model
            get_user_model().objects.create_superuser(username="admin", password="admin123", email="admin@example.com")
            self.client.login(username="admin", password="admin123")

        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, 'id="add-experience-modal"')
        self.assertContains(response, 'id="experience-form"')
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_experience_json_includes_primary_key_for_actions(self):
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 200)
        item = response.json()[0]
        self.assertEqual(item["pk"], str(self.experience.pk))
        self.assertEqual(item["fields"]["title"], self.experience.title)

    def test_experience_form_strips_html_input(self):
        form = ExperienceForm(
            data={
                "title": "<script>alert('xss')</script>Pengalaman Baru",
                "description": "<img src=x onerror=alert('xss')>deskripsi aman",
                "category": "internship",
                "ended_at": "",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["title"], "Pengalaman Baru")
        self.assertEqual(form.cleaned_data["description"], "deskripsi aman")

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))
        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")


class AboutTest(TestCase):
    def setUp(self):
        self.gallery_item = GalleryItem.objects.create(
            title="Main futsal bareng temen",
            caption="Hobi mingguan yang jarang bolong",
            media_type="photo",
            category="hobby",
            media_url="https://example.com/futsal.jpg",
        )

    def test_about_url_is_accessible(self):
        # Kasus 1: URL dapat diakses dan menggunakan template yang tepat
        response = self.client.get(reverse("main:show_about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")

    def test_about_page_shows_create_modal_for_superuser(self):
        user = get_user_model().objects.create_superuser(
            username="gallery-admin",
            password="securepass123",
            email="gallery-admin@example.com",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("main:show_about"))

        self.assertContains(response, 'id="add-gallery-item-modal"')
        self.assertContains(response, 'id="gallery-item-form"')
        self.assertContains(response, reverse("main:create_gallery_item_ajax"))

    def test_superuser_can_create_gallery_item_with_ajax(self):
        user = get_user_model().objects.create_superuser(
            username="gallery-creator",
            password="securepass123",
            email="gallery-creator@example.com",
        )
        self.client.force_login(user)
        upload = SimpleUploadedFile("memory.jpg", b"fake image data", content_type="image/jpeg")

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse("main:create_gallery_item_ajax"),
                    {
                        "title": "A new memory",
                        "caption": "A caption",
                        "media_type": "photo",
                        "category": "hobby",
                        "media_file": upload,
                    },
                )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(GalleryItem.objects.filter(title="A new memory").exists())

    def test_gallery_item_model(self):
        self.assertEqual(str(self.gallery_item), "Main futsal bareng temen")
        self.assertEqual(self.gallery_item.category, "hobby")
        self.assertEqual(self.gallery_item.media_type, "photo")

    def test_about_page_shows_gallery_data(self):
        # Kasus 2: data model muncul di halaman HTML ketika ada data
        response = self.client.get(reverse("main:show_about"))
        self.assertContains(response, self.gallery_item.title)
        self.assertContains(response, self.gallery_item.caption)
        self.assertContains(response, "Hobby")  # hasil get_category_display
        self.assertContains(response, self.gallery_item.media_url)

    def test_empty_about_page(self):
        # Kasus 3: pesan kondisi kosong muncul ketika belum ada data
        GalleryItem.objects.all().delete()
        response = self.client.get(reverse("main:show_about"))
        self.assertContains(response, "Belum ada item galeri yang ditambahkan.")
        self.assertNotContains(response, self.gallery_item.title)


class AuthFlowTest(TestCase):
    def test_login_page_does_not_show_stale_messages(self):
        response = self.client.get(reverse("main:login"))
        request = response.wsgi_request
        storage = FallbackStorage(request)
        storage.add(messages.SUCCESS, "Pesan lama dari aksi sebelumnya")
        request.session.modified = True

        response = self.client.get(reverse("main:login"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pesan lama dari aksi sebelumnya")


class EditorPermissionTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.editor = self.User.objects.create_user(username="editor", password="securepass123")

        experience_ct = ContentType.objects.get(app_label="main", model="experience")
        gallery_ct = ContentType.objects.get(app_label="main", model="galleryitem")

        permissions = Permission.objects.filter(
            content_type__in=[experience_ct, gallery_ct],
            codename__in=[
                "add_experience",
                "change_experience",
                "delete_experience",
                "add_galleryitem",
                "change_galleryitem",
                "delete_galleryitem",
            ],
        )
        self.editor.user_permissions.set(permissions)

    def test_editor_with_manage_permission_can_access_experience_form(self):
        self.client.login(username="editor", password="securepass123")
        response = self.client.get(reverse("main:create_experience"))
        self.assertEqual(response.status_code, 200)

    def test_editor_with_manage_permission_can_access_about_form(self):
        self.client.login(username="editor", password="securepass123")
        response = self.client.get(reverse("main:create_gallery_item"))
        self.assertEqual(response.status_code, 200)