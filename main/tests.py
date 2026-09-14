from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

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