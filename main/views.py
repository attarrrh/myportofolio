from django.shortcuts import render
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

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


def show_experience(request):
    context = {
        "name": "Attar",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_about(request):
    context = {
        "name": "Attar Rais Hakam",
        "gallery_list": GalleryItem.objects.all(),
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