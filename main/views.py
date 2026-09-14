from django.shortcuts import render

from main.models import Experience, GalleryItem


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