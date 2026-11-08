"""Optional Chrome integration: TUTORIAL7_BROWSER_VERIFY=1 python manage.py test main.tests_browser."""
import os
import tempfile
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, override_settings

from main.models import Experience, GalleryItem


@skipUnless(os.getenv("TUTORIAL7_BROWSER_VERIFY") == "1", "Opt-in local Chrome verification")
class Tutorial7BrowserTest(StaticLiveServerTestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("browser-owner", "owner@example.com", "test-password")
        self.viewer = User.objects.create_user("browser-viewer")
        self.editor = User.objects.create_user("browser-editor")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.gallery = GalleryItem.objects.create(title="Browser gallery", media_url="https://example.com/a.jpg")
        Experience.objects.create(title="Browser experience", description="Existing details")

    def test_ajax_crud_search_validation_star_upload_and_roles(self):
        from playwright.sync_api import expect, sync_playwright

        sessions = []
        for user in (self.owner, self.viewer, self.editor):
            client = Client()
            client.force_login(user)
            sessions.append(client.cookies[settings.SESSION_COOKIE_NAME].value)
        owner_session, viewer_session, editor_session = sessions
        errors = []
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            with sync_playwright() as automation:
                browser = automation.chromium.launch(channel="chrome", headless=True)
                context = browser.new_context()
                context.route("https://**/*", lambda route: route.abort())
                context.add_cookies([{"name": settings.SESSION_COOKIE_NAME, "value": owner_session, "url": self.live_server_url}])
                page = context.new_page()
                page.on("pageerror", lambda error: errors.append(str(error)))
                requests = []
                page.on("request", lambda request: requests.append((request.method, request.url)))
                page.goto(self.live_server_url + "/projects/")
                page.get_by_role("button", name="Tambah Project", exact=True).click()
                form = page.locator("#project-form")
                form.locator('[name="title"]').fill("   ")
                form.locator('[name="description"]').fill("Description")
                form.locator('[name="tech_stack"]').fill("Django")
                form.get_by_role("button", name="Simpan", exact=True).click()
                expect(page.locator("#toast-message")).to_contain_text("title")
                form.locator('[name="title"]').fill("Browser project")
                form.get_by_role("button", name="Simpan", exact=True).click()
                expect(page.locator("#projects-list h2")).to_have_text("Browser project")
                self.assertTrue(page.url.endswith("/projects/"))
                page.locator('[data-action="edit"]').click()
                form.locator('[name="title"]').fill("Edited project")
                form.get_by_role("button", name="Simpan", exact=True).click()
                expect(page.locator("#projects-list h2")).to_have_text("Edited project")
                page.locator('[data-action="star"]').click()
                expect(page.locator('[data-action="star"]')).to_have_attribute("aria-pressed", "true")
                search = page.locator('#project-search [name="title"]')
                search.fill("no matching project")
                expect(page.locator("#projects-list")).to_contain_text("Tidak ada project")
                search.fill("Edited")
                expect(page.locator("#projects-list h2")).to_have_text("Edited project")
                page.once("dialog", lambda dialog: dialog.accept())
                page.locator('[data-action="delete"]').click()
                expect(page.locator("#projects-list")).to_contain_text("Tidak ada project")
                self.assertTrue(any(method == "PATCH" and "/api/v1/projects/" in url for method, url in requests))
                self.assertTrue(any(method == "DELETE" and "/api/v1/projects/" in url for method, url in requests))
                page.goto(self.live_server_url + "/experience/")
                expect(page.locator(".exp-title")).to_contain_text("Browser experience")
                page.get_by_role("button", name="Tambah Experience", exact=True).click()
                exp = page.locator("#experience-form")
                exp.locator('[name="title"]').fill("Added through DRF")
                exp.locator('[name="description"]').fill("Uploaded from the existing modal")
                exp.locator('[name="media_files"]').set_input_files({"name": "proof.pdf", "mimeType": "application/pdf", "buffer": b"%PDF-1.4 test"})
                exp.get_by_role("button", name="Tambah Experience", exact=True).click()
                expect(page.locator("#experience-list")).to_contain_text("Added through DRF")
                page.goto(self.live_server_url + "/about/")
                expect(page.locator("#gallery-list h3")).to_have_text("Browser gallery")
                page.get_by_role("button", name="Tambah Item", exact=True).click()
                gallery = page.locator("#gallery-item-form")
                gallery.locator('[name="title"]').fill("Uploaded gallery")
                gallery.locator('[name="media_file"]').set_input_files({"name": "photo.jpg", "mimeType": "image/jpeg", "buffer": b"image test"})
                gallery.get_by_role("button", name="Tambah Item", exact=True).click()
                expect(page.locator("#gallery-list")).to_contain_text("Uploaded gallery")
                for session, can_edit in ((viewer_session, False), (editor_session, True)):
                    context.add_cookies([{"name": settings.SESSION_COOKIE_NAME, "value": session, "url": self.live_server_url}])
                    page.goto(self.live_server_url + "/about/")
                    expect(page.locator("#gallery-list .gallery-card")).to_have_count(2)
                    expect(page.get_by_role("button", name="Tambah Item", exact=True)).to_have_count(0)
                    expect(page.locator("#gallery-list").get_by_role("link", name="Edit", exact=True)).to_have_count(2 if can_edit else 0)
                    expect(page.locator("#gallery-list").get_by_role("button", name="Hapus", exact=True)).to_have_count(0)
                context.clear_cookies()
                page.goto(self.live_server_url + "/projects/")
                expect(page.get_by_role("button", name="Tambah Project", exact=True)).to_have_count(0)
                page.goto(self.live_server_url + "/experience/")
                expect(page.locator("#experience-list")).to_contain_text("Browser experience")
                browser.close()
        self.assertEqual(errors, [])

    def test_assignment6_gallery_edit_star_errors_and_delete_without_reload(self):
        from playwright.sync_api import expect, sync_playwright

        sessions = {}
        for role, user in (("owner", self.owner), ("viewer", self.viewer), ("editor", self.editor)):
            client = Client()
            client.force_login(user)
            sessions[role] = client.cookies[settings.SESSION_COOKIE_NAME].value
        # Old data must also be rendered as text, even if it bypassed the serializer.
        self.gallery.caption = '<img src=x onerror="window.xssExecuted=true">'
        self.gallery.save()
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            with sync_playwright() as automation:
                browser = automation.chromium.launch(channel="chrome", headless=True)
                context = browser.new_context()
                context.route("https://**/*", lambda route: route.abort())
                page = context.new_page()
                errors, writes = [], []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("request", lambda request: writes.append(request) if request.method in ("POST", "PATCH", "DELETE") else None)

                def login(role):
                    context.add_cookies([{"name": settings.SESSION_COOKIE_NAME, "value": sessions[role], "url": self.live_server_url}])

                login("owner")
                page.goto(self.live_server_url + "/about/")
                expect(page.locator("#gallery-list")).to_contain_text(self.gallery.caption)
                expect(page.locator(".gallery-info p img")).to_have_count(0)
                self.assertIsNone(page.evaluate("window.xssExecuted"))

                # A URL-only item can be edited without forcing a new file upload.
                page.get_by_role("link", name="Edit", exact=True).click()
                edit = page.locator('[data-api-form]')
                expect(edit.locator('[name="media_file"]')).not_to_have_attribute("required", "")
                page.evaluate("window.documentMarker = 'unchanged'")
                edit.locator('[name="caption"]').fill("<b>Edited by owner</b>")
                edit.get_by_role("button", name="Simpan Perubahan").click()
                expect(page.locator("#toast-title")).to_have_text("Sukses")
                self.assertEqual(page.evaluate("window.documentMarker"), "unchanged")

                page.goto(self.live_server_url + "/about/")
                expect(page.locator("#gallery-list")).to_contain_text("Edited by owner")
                page.get_by_role("button", name="Tambah Item", exact=True).click()
                form = page.locator("#gallery-item-form")
                form.locator('[name="title"]').fill("<b>Assignment gallery</b>")
                form.locator('[name="media_file"]').set_input_files({"name": "assignment.jpg", "mimeType": "image/jpeg", "buffer": b"image"})
                page.evaluate("window.documentMarker = 'unchanged'")
                form.get_by_role("button", name="Tambah Item", exact=True).click()
                expect(page.locator("#gallery-list")).to_contain_text("Assignment gallery")
                self.assertEqual(page.evaluate("window.documentMarker"), "unchanged")

                # Viewer and Editor can star; only Editor has an edit link.
                for role in ("viewer", "editor"):
                    login(role)
                    page.goto(self.live_server_url + "/about/")
                    expect(page.locator(".gallery-card")).to_have_count(2)
                    expect(page.get_by_role("button", name="Tambah Item", exact=True)).to_have_count(0)
                    expect(page.get_by_role("button", name="Hapus", exact=True)).to_have_count(0)
                    star = page.locator(".button-like").first
                    star.click()
                    expect(star).to_have_attribute("aria-pressed", "true")
                    star.click()
                    expect(star).to_have_attribute("aria-pressed", "false")

                page.get_by_role("link", name="Edit", exact=True).first.click()
                edit = page.locator('[data-api-form]')
                page.evaluate("window.documentMarker = 'unchanged'")
                edit.locator('[name="title"]').fill("   ")
                edit.get_by_role("button", name="Simpan Perubahan").click()
                expect(page.locator("#toast-title")).to_have_text("Gagal menyimpan data")
                expect(page.locator("#toast-message")).to_contain_text("title")
                edit.locator('[name="title"]').fill("Edited by Editor")
                edit.get_by_role("button", name="Simpan Perubahan").click()
                expect(page.locator("#toast-title")).to_have_text("Sukses")
                self.assertEqual(page.evaluate("window.documentMarker"), "unchanged")

                # API errors must reach the toast instead of navigating to an API URL.
                page.route("**/api/v1/gallery/*/", lambda route: route.fulfill(
                    status=403, content_type="application/json", body='{"detail":"Permission denied."}'
                ))
                edit.get_by_role("button", name="Simpan Perubahan").click()
                expect(page.locator("#toast-message")).to_have_text("Permission denied.")
                self.assertEqual(page.evaluate("window.documentMarker"), "unchanged")
                page.unroute("**/api/v1/gallery/*/")

                login("owner")
                page.goto(self.live_server_url + "/about/")
                target = page.locator(".gallery-card").filter(has=page.get_by_role("heading", name="Edited by Editor", exact=True))
                expect(target).to_have_count(1)
                page.evaluate("window.documentMarker = 'unchanged'")
                page.once("dialog", lambda dialog: dialog.accept())
                target.get_by_role("button", name="Hapus", exact=True).click()
                expect(page.locator(".gallery-card")).to_have_count(1)
                self.assertEqual(page.evaluate("window.documentMarker"), "unchanged")

                context.clear_cookies()
                page.goto(self.live_server_url + "/about/")
                expect(page.locator(".button-like")).to_be_disabled()
                expect(page.get_by_role("link", name="Edit", exact=True)).to_have_count(0)
                self.assertTrue(any(request.method == "PATCH" for request in writes))
                self.assertTrue(any(request.method == "DELETE" for request in writes))
                self.assertTrue(all(request.headers.get("x-csrftoken") for request in writes if "/api/v1/" in request.url))
                self.assertEqual(errors, [])
                browser.close()
