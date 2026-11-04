from django.urls import path
from main import api_views

app_name = "api"

urlpatterns = [
    path("projects/", api_views.project_list, name="project-list"),
    path("projects/<uuid:project_id>/", api_views.project_detail, name="project-detail"),
    path("projects/<uuid:project_id>/star/", api_views.project_star, name="project-star"),
    path("gallery/", api_views.gallery_list, name="gallery-list"),
    path("gallery/<uuid:item_id>/", api_views.gallery_detail, name="gallery-detail"),
    path("gallery/<uuid:item_id>/star/", api_views.gallery_star, name="gallery-star"),
    path("experiences/", api_views.experience_list, name="experience-list"),
    path("experiences/<uuid:experience_id>/", api_views.experience_detail, name="experience-detail"),
]
