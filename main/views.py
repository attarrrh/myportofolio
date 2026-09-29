import datetime
from django.shortcuts import render
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.decorators.http import require_POST
from django.template.defaultfilters import date as date_filter

from main.models import Experience, ExperienceMedia, GalleryItem
from main.forms import ExperienceForm, GalleryItemForm


def user_can_manage_experience(user):
    return (
        user.is_superuser
        or user.has_perm("main.add_experience")
        or user.has_perm("main.change_experience")
        or user.has_perm("main.delete_experience")
    )


def user_can_manage_gallery(user):
    return (
        user.is_superuser
        or user.has_perm("main.add_galleryitem")
        or user.has_perm("main.change_galleryitem")
        or user.has_perm("main.delete_galleryitem")
    )


def show_main(request):
    last_login = request.COOKIES.get(
        "last_login", "Belum ada sesi login / Cookie tidak ditemukan"
    )
    context = {
        "full_name": "ATTAR RAIS HAKAM",
        "name": "Attar",
        "npm": "2506656495",
        "study_program": "Bachelor of Information System",
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.prefetch_related("media").all()
 
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)
 
    data = []
    for experience in experiences:
        started = date_filter(experience.started_at, "M Y")
        ended = "Present" if experience.is_ongoing else date_filter(experience.ended_at, "M Y")
 
        data.append({
            "pk": str(experience.id),
            "fields": {
                "title": experience.title,
                "description": experience.description,
                "category_display": experience.get_category_display(),
                "started": started,
                "ended": ended,
                "is_ongoing": experience.is_ongoing,
                "media": [
                    {
                        "url": m.file.url,
                        "filename": m.filename,
                        "is_image": m.is_image,
                        "is_video": m.is_video,
                    }
                    for m in experience.media.all()
                ],
            },
        })
 
    return JsonResponse(data, safe=False)


def get_gallery_json(request):
    title_query = request.GET.get("title", "").strip()
    items = GalleryItem.objects.all()

    if title_query:
        items = items.filter(title__icontains=title_query)

    items_json = serializers.serialize("json", items)
    return HttpResponse(items_json, content_type="application/json")


def show_experience(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.prefetch_related("media").all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    context = {
        "name": "Attar",
        "title_query": title_query,
        "experience_list": experiences,
        "form": ExperienceForm(),
    }
    return render(request, "experience.html", context)


def show_about(request):
    title_query = request.GET.get("title", "").strip()
    items = GalleryItem.objects.all()

    if title_query:
        items = items.filter(title__icontains=title_query)

    context = {
        "name": "Attar Rais Hakam",
        "gallery_list": items,
        "title_query": title_query,
    }
    return render(request, "about.html", context)


@login_required(login_url="/login/")
def create_experience(request):
    if not user_can_manage_experience(request.user):
        raise PermissionDenied

    form = ExperienceForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        experience = form.save()
        for f in form.cleaned_data["media_files"]:
            ExperienceMedia.objects.create(experience=experience, file=f)
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {"name": "Attar", "form": form}
    return render(request, "experience_form.html", context)

@require_POST
def create_experience_ajax(request):
    user = request.user
    if not (user.is_superuser or user.has_perm("main.add_experience")):
        return JsonResponse(
            {"message": "Kamu tidak punya izin untuk menambahkan experience."},
            status=403,
        )
 
    form = ExperienceForm(request.POST, request.FILES)
    if form.is_valid():
        experience = form.save()
        for f in form.cleaned_data["media_files"]:
            ExperienceMedia.objects.create(experience=experience, file=f)
        return JsonResponse(
            {"message": "Experience berhasil ditambahkan.", "pk": str(experience.id)},
            status=201,
        )
 
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not user_can_manage_experience(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, request.FILES or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        experience = form.save()
        for f in form.cleaned_data["media_files"]:
            ExperienceMedia.objects.create(experience=experience, file=f)
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {"name": "Attar", "form": form, "experience": experience}
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not user_can_manage_experience(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        for m in experience.media.all():
            m.file.delete(save=False)  # hapus file fisiknya juga
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")

    return redirect("main:show_experience")


@login_required(login_url="/login/")
def delete_experience_media(request, media_id):
    if not user_can_manage_experience(request.user):
        raise PermissionDenied

    media = get_object_or_404(ExperienceMedia, pk=media_id)
    experience_id = media.experience_id

    if request.method == "POST":
        media.file.delete(save=False)
        media.delete()
        messages.success(request, "File berhasil dihapus!")

    return redirect("main:update_experience", experience_id=experience_id)

@login_required(login_url="/login/")
def create_gallery_item(request):
    if not user_can_manage_gallery(request.user):
        raise PermissionDenied

    form = GalleryItemForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item galeri berhasil ditambahkan!")
        return redirect("main:show_about")

    context = {"name": "Attar", "form": form}
    return render(request, "about_form.html", context)



@login_required(login_url="/login/")
def delete_gallery_item(request, item_id):
    if not user_can_manage_gallery(request.user):
        raise PermissionDenied
    
    item = get_object_or_404(GalleryItem, pk=item_id)

    if request.method == "POST":
        item.delete()
        messages.success(request, "Item galeri berhasil dihapus!")
        return redirect("main:show_about")

    return redirect("main:show_about")


@login_required(login_url="/login/")
def update_gallery_item(request, item_id):
    if not user_can_manage_gallery(request.user):
        raise PermissionDenied

    item = get_object_or_404(GalleryItem, pk=item_id)
    form = GalleryItemForm(request.POST or None, request.FILES or None, instance=item)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item galeri berhasil diperbarui!")
        return redirect("main:show_about")

    context = {"name": "Attar", "form": form, "item": item}
    return render(request, "about_form.html", context)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Attar",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    if request.method == "GET":
        list(get_messages(request))

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response

    context = {
        "name": "Attar",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


def get_gallery_json(request):
    title_query = request.GET.get("title", "").strip()
    items = GalleryItem.objects.all()

    if title_query:
        items = items.filter(title__icontains=title_query)

    items_json = serializers.serialize(
        "json", items, use_natural_foreign_keys=True
    )
    return HttpResponse(items_json, content_type="application/json")


@login_required(login_url="/login/")
def toggle_like(request, item_id):
    item = get_object_or_404(GalleryItem, pk=item_id)

    if request.method == "POST":
        if request.user in item.liked_by.all():
            item.liked_by.remove(request.user)
        else:
            item.liked_by.add(request.user)

    return redirect("main:show_about")