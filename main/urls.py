from django.urls import path

from main.views import show_main, show_experience, show_about, create_experience, create_gallery_item

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("about/", show_about, name="show_about"),
    path("experience/add/", create_experience, name="create_experience"),
    path("about/add/", create_gallery_item, name="create_gallery_item"),
]