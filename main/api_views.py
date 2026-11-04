from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Experience, GalleryItem, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly
from main.serializers import ExperienceSerializer, GalleryItemSerializer, ProjectSerializer


def collection(request, queryset, serializer_class):
    if request.method in ("GET", "HEAD"):
        title = request.query_params.get("title", "").strip()
        if title:
            queryset = queryset.filter(title__icontains=title)
        return Response(serializer_class(queryset, many=True, context={"request": request}).data)
    serializer = serializer_class(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def detail(request, queryset, pk, serializer_class):
    instance = get_object_or_404(queryset, pk=pk)
    if request.method in ("GET", "HEAD"):
        return Response(serializer_class(instance, context={"request": request}).data)
    if request.method == "DELETE":
        if isinstance(instance, Experience):
            for media in instance.media.all():
                media.file.delete(save=False)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = serializer_class(instance, data=request.data, partial=request.method == "PATCH",
                                  context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    return collection(request, Project.objects.prefetch_related("starred_by").order_by("title", "id"), ProjectSerializer)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    return detail(request, Project.objects.prefetch_related("starred_by"), project_id, ProjectSerializer)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def project_star(request, project_id):
    project = get_object_or_404(Project.objects.select_for_update(), pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    return Response(ProjectSerializer(project, context={"request": request}).data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def gallery_list(request):
    return collection(request, GalleryItem.objects.prefetch_related("liked_by").order_by("-created_at", "id"), GalleryItemSerializer)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def gallery_detail(request, item_id):
    return detail(request, GalleryItem.objects.prefetch_related("liked_by"), item_id, GalleryItemSerializer)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def gallery_star(request, item_id):
    item = get_object_or_404(GalleryItem.objects.select_for_update(), pk=item_id)
    if item.liked_by.filter(pk=request.user.pk).exists():
        item.liked_by.remove(request.user)
    else:
        item.liked_by.add(request.user)
    return Response(GalleryItemSerializer(item, context={"request": request}).data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    return collection(request, Experience.objects.prefetch_related("media").order_by("title", "id"), ExperienceSerializer)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    return detail(request, Experience.objects.prefetch_related("media"), experience_id, ExperienceSerializer)


# Function-based DRF views expose their APIView class through .cls.
for view in (gallery_list, gallery_detail):
    view.cls.resource_model = GalleryItem
for view in (experience_list, experience_detail):
    view.cls.resource_model = Experience
