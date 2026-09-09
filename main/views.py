from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "name": "Attar",
        "npm": "2506656495",
        "study_program": "Bachelor of Information System",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Attar",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)