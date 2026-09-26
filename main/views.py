import datetime
from django.shortcuts import render
from django.contrib import messages
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from main.models import Experience, GalleryItem
from main.forms import ExperienceForm, GalleryItemForm



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
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")


def get_gallery_json(request):
    title_query = request.GET.get("title", "").strip()
    items = GalleryItem.objects.all()

    if title_query:
        items = items.filter(title__icontains=title_query)

    items_json = serializers.serialize("json", items)
    return HttpResponse(items_json, content_type="application/json")


def show_experience(request):
    json_response = get_experience_json(request)
    experiences = serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )
    experiences = [e.object for e in experiences]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Attar",
        "experience_list": experiences,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)


def show_about(request):
    json_response = get_gallery_json(request)
    items = serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )
    items = [i.object for i in items]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Attar Rais Hakam",
        "gallery_list": items,
        "title_query": title_query,
    }
    return render(request, "about.html", context)


@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Attar",
        "form": form,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def create_gallery_item(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = GalleryItemForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item galeri berhasil ditambahkan!")
        return redirect("main:show_about")

    context = {
        "name": "Attar",
        "form": form,
    }
    return render(request, "about_form.html", context)


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")


@login_required(login_url="/login/")
def delete_gallery_item(request, item_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    item = get_object_or_404(GalleryItem, pk=item_id)

    if request.method == "POST":
        item.delete()
        messages.success(request, "Item galeri berhasil dihapus!")
        return redirect("main:show_about")

    return redirect("main:show_about")


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Attar",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def update_gallery_item(request, item_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    item = get_object_or_404(GalleryItem, pk=item_id)
    form = GalleryItemForm(request.POST or None, instance=item)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item galeri berhasil diperbarui!")
        return redirect("main:show_about")

    context = {
        "name": "Attar",
        "form": form,
        "item": item,
    }
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