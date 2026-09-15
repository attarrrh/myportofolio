from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_about,
    create_experience,
    create_gallery_item,
    get_experience_json,
    get_gallery_json,
    delete_experience,
    delete_gallery_item,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("about/", show_about, name="show_about"),
    path("experience/add/", create_experience, name="create_experience"),
    path("about/add/", create_gallery_item, name="create_gallery_item"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("api/gallery/", get_gallery_json, name="get_gallery_json"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("about/<uuid:item_id>/delete/", delete_gallery_item, name="delete_gallery_item"),
]