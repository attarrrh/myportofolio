import tempfile
import uuid
from django.contrib.auth.models import Group, Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from django.utils import timezone
from main.models import Experience, GalleryItem


class PortfolioAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("portfolio-owner", "owner@example.com", "test-password")
        self.editor = User.objects.create_user("portfolio-editor")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.viewer = User.objects.create_user("portfolio-viewer", password="test-password")
        self.experience = Experience.objects.create(title="Research", description="Existing experience")
        self.gallery = GalleryItem.objects.create(title="Holiday", caption="Existing gallery", media_url="https://example.com/photo.jpg")

    def resources(self):
        return [
            ("gallery", self.gallery, {"title": "New photo", "media_type": "photo", "media_url": "https://example.com/photo.jpg"}),
            ("experience", self.experience, {"title": "New role", "description": "New experience"}),
        ]

    def test_existing_sections_expose_public_flat_json_and_search(self):
        for name, instance, payload in self.resources():
            response = self.client.get(reverse(f"api:{name}-list"), {"title": instance.title.upper()})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data[0]["id"], str(instance.pk))
            self.assertNotIn("fields", response.data[0])
            self.assertEqual(self.client.get(reverse(f"api:{name}-list"), {"title": "no match"}).data, [])

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        for name, instance, payload in self.resources():
            detail = reverse(f"api:{name}-detail", args=[instance.pk])
            self.assertEqual(self.client.patch(detail, {"title": "Edited"}, format="json").status_code, 200)
            self.assertEqual(self.client.put(detail, payload, format="json").status_code, 200)
            self.assertEqual(self.client.post(reverse(f"api:{name}-list"), payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(detail).status_code, 403)
            instance.refresh_from_db()
            self.assertEqual(instance.title, payload["title"])

    def test_ordinary_user_cannot_update_existing_sections(self):
        self.client.force_authenticate(user=self.viewer)
        for name, instance, payload in self.resources():
            self.assertEqual(self.client.patch(reverse(f"api:{name}-detail", args=[instance.pk]), payload, format="json").status_code, 403)

    def test_change_permission_is_supported_without_editor_group(self):
        self.viewer.user_permissions.add(Permission.objects.get(codename="change_galleryitem"))
        self.client.force_authenticate(user=self.viewer)
        detail = reverse("api:gallery-detail", args=[self.gallery.pk])
        self.assertEqual(self.client.patch(detail, {"title": "Changed"}, format="json").status_code, 200)
        self.assertEqual(self.client.delete(detail).status_code, 403)

    def test_owner_can_create_and_delete_existing_section_resources(self):
        self.client.force_authenticate(user=self.owner)
        for name, instance, payload in self.resources():
            response = self.client.post(reverse(f"api:{name}-list"), payload, format="json")
            self.assertEqual(response.status_code, 201, response.data)
            deleted = self.client.delete(reverse(f"api:{name}-detail", args=[response.data["id"]]))
            self.assertEqual(deleted.status_code, 204)
            self.assertEqual(deleted.content, b"")

    def test_gallery_star_uses_existing_relation_and_ignores_forged_user(self):
        self.client.force_authenticate(user=self.viewer)
        url = reverse("api:gallery-star", args=[self.gallery.pk])
        response = self.client.post(url, {"user_id": self.owner.pk}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], self.viewer.username)
        self.assertFalse(self.gallery.liked_by.filter(pk=self.owner.pk).exists())
        self.assertFalse(self.client.post(url).data["is_starred"])

    def test_gallery_rejects_empty_title_unsafe_url_and_forged_star_fields(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("api:gallery-list")
        for data in ({"title": "<img src=x>", "media_url": "https://example.com/a.jpg"},
                     {"title": "Bad URL", "media_url": "javascript:alert(1)"}):
            self.assertEqual(self.client.post(url, data, format="json").status_code, 400)
        response = self.client.post(url, {"title": "Safe", "media_url": "https://example.com/a.jpg",
            "liked_by": [self.owner.pk], "star_count": 99, "is_starred": True}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)

    def test_multipart_uploads_and_existing_files_survive_partial_updates(self):
        self.client.force_authenticate(user=self.owner)
        with tempfile.TemporaryDirectory() as root, override_settings(MEDIA_ROOT=root):
            response = self.client.post(reverse("api:gallery-list"), {
                "title": "Uploaded", "media_type": "photo",
                "media_file": SimpleUploadedFile("photo.jpg", b"image", content_type="image/jpeg"),
            }, format="multipart")
            self.assertEqual(response.status_code, 201, response.data)
            self.assertIn("/media/gallery/", response.data["display_url"])
            url = reverse("api:gallery-detail", args=[response.data["id"]])
            self.assertEqual(self.client.patch(url, {"caption": "Updated"}, format="json").status_code, 200)
            response = self.client.post(reverse("api:experience-list"), {
                "title": "With attachment", "description": "Details",
                "media_files": [SimpleUploadedFile("doc.pdf", b"pdf", content_type="application/pdf")],
            }, format="multipart")
            self.assertEqual(response.status_code, 201, response.data)
            self.assertEqual(len(response.data["media"]), 1)

    def test_editor_html_form_is_available_but_create_and_delete_buttons_are_hidden(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(reverse("main:update_gallery_item", args=[self.gallery.pk])).status_code, 200)
        page = self.client.get(reverse("main:show_about"))
        self.assertNotContains(page, 'id="add-gallery-item-modal"')
        self.assertContains(page, 'data-can-delete="false"')

    def test_html_lists_reference_versioned_api_and_keep_legacy_routes(self):
        for page, route in (("show_experience", "experience-list"), ("show_about", "gallery-list"), ("show_projects", "project-list")):
            self.assertContains(self.client.get(reverse("main:" + page)), reverse("api:" + route))
        self.assertEqual(self.client.get(reverse("main:get_gallery_json")).status_code, 200)
        self.assertEqual(self.client.get(reverse("main:get_experience_json")).status_code, 200)

    def test_head_and_options_do_not_change_data(self):
        self.client.force_authenticate(user=self.editor)
        for name, instance, payload in self.resources():
            url = reverse(f"api:{name}-detail", args=[instance.pk])
            self.assertEqual(self.client.head(url).status_code, 200)
            self.assertEqual(self.client.options(url).status_code, 200)
            instance.refresh_from_db()
            self.assertNotEqual(instance.title, "Edited")

    def test_rejected_writes_preserve_database_for_guest_viewer_and_editor(self):
        for user in (None, self.viewer, self.editor):
            self.client.force_authenticate(user=user)
            for name, instance, payload in self.resources():
                model = type(instance)
                before = list(model.objects.order_by("pk").values())
                list_url = reverse(f"api:{name}-list")
                detail_url = reverse(f"api:{name}-detail", args=[instance.pk])
                requests = [("post", list_url, payload), ("delete", detail_url, {})]
                if user != self.editor:
                    requests += [("put", detail_url, payload), ("patch", detail_url, {"title": "Forged"})]
                for method, url, data in requests:
                    with self.subTest(role=user, resource=name, method=method):
                        response = getattr(self.client, method)(url, data, format="json")
                        self.assertEqual(response.status_code, 403)
                        self.assertEqual(list(model.objects.order_by("pk").values()), before)

    def test_gallery_guest_cannot_star_and_missing_data_returns_404(self):
        star = reverse("api:gallery-star", args=[self.gallery.pk])
        self.assertEqual(self.client.post(star).status_code, 403)
        self.assertEqual(self.gallery.liked_by.count(), 0)
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(self.client.get(star).status_code, 405)
        for name, instance, payload in self.resources():
            detail = reverse(f"api:{name}-detail", args=[uuid.uuid4()])
            self.assertEqual(self.client.get(detail).status_code, 404)
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(self.client.post(reverse("api:gallery-star", args=[uuid.uuid4()])).status_code, 404)

    def test_gallery_serialization_has_safe_read_only_star_fields(self):
        self.gallery.liked_by.add(self.viewer)
        for user in (None, self.viewer, self.editor, self.owner):
            self.client.force_authenticate(user=user)
            response = self.client.get(reverse("api:gallery-detail", args=[self.gallery.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["star_count"], 1)
            self.assertEqual(response.data["is_starred"], user == self.viewer)
            self.assertNotIn("liked_by", response.data)
            self.assertNotIn("password", response.data)
            self.assertNotIn("email", response.data)
            self.assertNotContains(response, self.viewer.password)
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(reverse("api:gallery-detail", args=[self.gallery.pk]), {
            "id": str(uuid.uuid4()), "star_count": 999, "is_starred": True,
            "liked_by": [self.owner.pk], "starred_by_names": "forged",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.gallery.pk))
        self.assertEqual(response.data["star_count"], 1)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(list(self.gallery.liked_by.all()), [self.viewer])

    def test_gallery_validation_cleans_text_and_rejects_without_saving(self):
        self.client.force_authenticate(user=self.owner)
        detail = reverse("api:gallery-detail", args=[self.gallery.pk])
        before = list(GalleryItem.objects.values())
        for data in ({"title": "<b></b>"}, {"title": "   "}, {"media_url": "javascript:alert(1)"}):
            response = self.client.patch(detail, data, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(list(GalleryItem.objects.values()), before)
        response = self.client.patch(detail, {
            "title": "<b>Holiday</b>",
            "caption": "&lt;script&gt;alert(1)&lt;/script&gt;<b>Safe caption</b>",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.gallery.refresh_from_db()
        self.assertEqual(self.gallery.title, "Holiday")
        self.assertEqual(self.gallery.caption, "Safe caption")

    def test_gallery_session_csrf_protects_crud_and_star(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="portfolio-owner", password="test-password"))
        list_url = reverse("api:gallery-list")
        detail = reverse("api:gallery-detail", args=[self.gallery.pk])
        star = reverse("api:gallery-star", args=[self.gallery.pk])
        before = list(GalleryItem.objects.values())
        for method, url, payload in [
            ("post", list_url, {"title": "New", "media_url": "https://example.com/a.jpg"}),
            ("put", detail, {"title": "Changed", "media_url": "https://example.com/a.jpg"}),
            ("patch", detail, {"title": "Changed"}), ("delete", detail, {}), ("post", star, {}),
        ]:
            response = getattr(client, method)(url, payload, format="json")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(list(GalleryItem.objects.values()), before)
            self.assertEqual(self.gallery.liked_by.count(), 0)
        # A normal page must supply a token even when there is no create modal.
        self.assertTrue(client.login(username="portfolio-viewer", password="test-password"))
        self.assertEqual(client.get(reverse("main:show_about")).status_code, 200)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(star, HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.assertTrue(self.gallery.liked_by.filter(pk=self.viewer.pk).exists())

    def test_legacy_views_do_not_bypass_api_roles(self):
        # Old Django add/delete permissions must not grant broader access than DRF.
        self.editor.user_permissions.set(Permission.objects.filter(content_type__app_label="main"))
        self.client.force_login(self.editor)
        for name, instance, payload in self.resources():
            gallery = name == "gallery"
            create = "create_gallery_item" if gallery else "create_experience"
            delete = "delete_gallery_item" if gallery else "delete_experience"
            before = list(type(instance).objects.values())
            self.assertEqual(self.client.get(reverse("main:" + create)).status_code, 403)
            self.assertEqual(self.client.post(reverse("main:" + create), payload).status_code, 403)
            self.assertEqual(self.client.post(reverse("main:" + create + "_ajax"), payload).status_code, 403)
            self.assertEqual(self.client.post(reverse("main:" + delete, args=[instance.pk])).status_code, 403)
            self.assertEqual(list(type(instance).objects.values()), before)

    def test_edit_pages_submit_to_drf_and_optional_date_can_be_cleared(self):
        self.client.force_login(self.editor)
        for name, instance, payload in self.resources():
            route = "update_gallery_item" if name == "gallery" else "update_experience"
            response = self.client.get(reverse("main:" + route, args=[instance.pk]))
            self.assertContains(response, 'data-api-method="PATCH"')
            self.assertContains(response, reverse(f"api:{name}-detail", args=[instance.pk]))
            self.assertContains(response, "js/resource-form.js")
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.patch(reverse("api:experience-detail", args=[self.experience.pk]), {"ended_at": ""}, format="multipart")
        self.assertEqual(response.status_code, 200, response.data)
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)
