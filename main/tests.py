from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
import tempfile

from main.forms import ExperienceForm, GalleryItemForm
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
        self.assertNotContains(response, self.experience.title)
        self.assertNotContains(response, self.experience.description)
        self.assertContains(response, "Memuat data experience...")
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
        self.assertContains(response, "Memuat data experience...")
        self.assertEqual(self.client.get(reverse("main:get_experience_json")).json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))
        self.assertFalse(self.experience.is_ongoing)
        data = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]
        self.assertFalse(data["is_ongoing"])
        self.assertTrue(data["ended"])


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
        self.assertContains(response, reverse("api:gallery-list"))

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
        # Data hanya muncul lewat JSON, halaman merender kerangka.
        response = self.client.get(reverse("main:show_about"))
        self.assertNotContains(response, self.gallery_item.title)
        self.assertNotContains(response, self.gallery_item.caption)
        data = self.client.get(reverse("main:get_gallery_json")).json()[0]["fields"]
        self.assertEqual(data["title"], self.gallery_item.title)
        self.assertEqual(data["media_url"], self.gallery_item.media_url)

    def test_empty_about_page(self):
        # Kasus 3: pesan kondisi kosong muncul ketika belum ada data
        GalleryItem.objects.all().delete()
        response = self.client.get(reverse("main:show_about"))
        self.assertContains(response, "Memuat data galeri...")
        self.assertEqual(self.client.get(reverse("main:get_gallery_json")).json(), [])
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
        self.assertEqual(response.status_code, 403)
        experience = Experience.objects.create(title="Edit", description="Details")
        self.assertEqual(self.client.get(reverse("main:update_experience", args=[experience.pk])).status_code, 200)

    def test_editor_with_manage_permission_can_access_about_form(self):
        self.client.login(username="editor", password="securepass123")
        response = self.client.get(reverse("main:create_gallery_item"))
        self.assertEqual(response.status_code, 403)
        item = GalleryItem.objects.create(title="Edit", media_url="https://example.com/a.jpg")
        self.assertEqual(self.client.get(reverse("main:update_gallery_item", args=[item.pk])).status_code, 200)


class AjaxChecklistTest(TestCase):
    def setUp(self):
        self.viewer = get_user_model().objects.create_user(username="viewer")
        self.editor = get_user_model().objects.create_user(username="ajax-editor")
        self.editor.user_permissions.set(Permission.objects.filter(
            codename__in=["add_experience", "add_galleryitem"], content_type__app_label="main"
        ))
        self.admin = get_user_model().objects.create_superuser(username="ajax-admin", email="admin@example.com")
        self.experience = Experience.objects.create(title="Research", description="Details")
        self.gallery = GalleryItem.objects.create(title="Holiday", caption="Beach", media_url="https://example.com/a.jpg")
        self.gallery.liked_by.add(self.viewer)

    def test_public_lists_and_json_for_every_role(self):
        for user in [None, self.viewer, self.editor, self.admin]:
            self.client.logout()
            if user:
                self.client.force_login(user)
            for name in ["show_experience", "show_about", "get_experience_json", "get_gallery_json"]:
                with self.subTest(role=user, endpoint=name):
                    response = self.client.get(reverse("main:" + name))
                    self.assertEqual(response.status_code, 200)
            state = self.client.get(reverse("main:get_gallery_json")).json()[0]["fields"]
            self.assertEqual(state["star_count"], 1)
            self.assertEqual(state["is_starred"], user == self.viewer)

    def test_search_filters_title_and_returns_empty_array(self):
        for endpoint, title in [("get_experience_json", "Research"), ("get_gallery_json", "Holiday")]:
            url = reverse("main:" + endpoint)
            self.assertEqual(len(self.client.get(url, {"title": title.lower()}).json()), 1)
            self.assertEqual(self.client.get(url, {"title": "no match"}).json(), [])

    def test_create_denies_visitor_viewer_and_change_only_user(self):
        change_only = get_user_model().objects.create_user(username="change-only")
        change_only.user_permissions.set(Permission.objects.filter(
            codename__in=["change_experience", "change_galleryitem"], content_type__app_label="main"
        ))
        for user in [None, self.viewer, self.editor, change_only]:
            self.client.logout()
            if user:
                self.client.force_login(user)
            for endpoint in ["create_experience_ajax", "create_gallery_item_ajax"]:
                response = self.client.post(reverse("main:" + endpoint), {})
                self.assertEqual(response.status_code, 403)
                self.assertIn("message", response.json())

    def test_create_validates_and_returns_201_for_owner(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            for user in [self.admin]:
                self.client.force_login(user)
                for endpoint in ["create_experience_ajax", "create_gallery_item_ajax"]:
                    url = reverse("main:" + endpoint)
                    self.assertEqual(self.client.get(url).status_code, 405)
                    invalid = self.client.post(url, {})
                    self.assertEqual(invalid.status_code, 400)
                    self.assertIn("title", invalid.json()["errors"])
                    data = {"title": "<b>New</b>", "category": "hobby", "caption": "<img src=x onerror=alert(1)>safe", "media_type": "photo"}
                    if endpoint == "create_experience_ajax":
                        data.update(category="research", description="<b>Details</b>")
                    else:
                        data["media_file"] = SimpleUploadedFile("new.jpg", b"photo", content_type="image/jpeg")
                    response = self.client.post(url, data)
                    self.assertEqual(response.status_code, 201, response.content)
                    model = Experience if endpoint == "create_experience_ajax" else GalleryItem
                    saved = model.objects.get(pk=response.json()["pk"])
                    self.assertEqual(saved.title, "New")
                    self.assertEqual(saved.description if model == Experience else saved.caption, "Details" if model == Experience else "safe")

    def test_post_requires_real_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        page = client.get(reverse("main:show_experience"))
        self.assertEqual(page.status_code, 200)
        token = client.cookies["csrftoken"].value
        for endpoint in ["create_experience_ajax", "create_gallery_item_ajax"]:
            url = reverse("main:" + endpoint)
            self.assertEqual(client.post(url, {}).status_code, 403)
            response = client.post(url, {}, HTTP_X_CSRFTOKEN=token)
            self.assertEqual(response.status_code, 400)
            self.assertIn("errors", response.json())

    def test_star_toggle_and_anonymous_denial(self):
        url = reverse("main:toggle_like", args=[self.gallery.pk])
        self.assertEqual(self.client.post(url, HTTP_ACCEPT="application/json").status_code, 403)
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.get(url).status_code, 405)
        for count, starred in [(0, False), (1, True)]:
            response = self.client.post(url, HTTP_ACCEPT="application/json")
            self.assertEqual(response.json(), {"star_count": count, "is_starred": starred})

    def test_encoded_html_and_gallery_caption_are_cleaned(self):
        upload = SimpleUploadedFile("clean.jpg", b"photo", content_type="image/jpeg")
        form = GalleryItemForm(data={
            "title": "&lt;script&gt;alert(1)&lt;/script&gt;Title",
            "caption": "<svg onload=alert(1)>bad</svg><b>Caption</b>",
            "category": "hobby", "media_type": "photo",
        }, files={"media_file": upload})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["title"], "Title")
        self.assertEqual(form.cleaned_data["caption"], "Caption")
