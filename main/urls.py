from django.urls import path

from main.views import (
    login_user,
    show_main,
    show_experience,
    show_about,
    create_experience,
    create_gallery_item,
    get_experience_json,
    get_gallery_json,
    delete_experience,
    delete_gallery_item,
    update_experience,
    update_gallery_item,
    register,
    login_user,
    logout_user,
    toggle_like,
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
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("about/<uuid:item_id>/edit/", update_gallery_item, name="update_gallery_item"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("about/<uuid:item_id>/like/", toggle_like, name="toggle_like"),
]