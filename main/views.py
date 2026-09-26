import datetime
from django.shortcuts import render
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from main.models import Experience, GalleryItem
from main.forms import ExperienceForm, GalleryItemForm



def show_main(request):
    context = {
        "full_name": "ATTAR RAIS HAKAM",
        "name": "Attar",
        "npm": "2506656495",
        "study_program": "Bachelor of Information System",
        # "bio": "I am a student at the University of Indonesia, majoring in Information Systems and my favorite class is kombistek",
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

    
def create_experience(request):
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


def create_gallery_item(request):
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

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")


def delete_gallery_item(request, item_id):
    item = get_object_or_404(GalleryItem, pk=item_id)

    if request.method == "POST":
        item.delete()
        messages.success(request, "Item galeri berhasil dihapus!")
        return redirect("main:show_about")

    return redirect("main:show_about")

def update_experience(request, experience_id):
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


def update_gallery_item(request, item_id):
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
        
        return response

    context = {
        "name": "Attar",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    return response