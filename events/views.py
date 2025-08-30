from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
import uuid
from .models import Events
from django.contrib.auth import get_user_model

User = get_user_model()


def home(request):
    page = request.GET.get("page", 1)
    category = (
        request.POST.get("category", "all")
        if request.method == "POST"
        else request.GET.get("category", "all")
    )

    events = (
        Events.objects.all().order_by("-created_at")
        if category == "all"
        else Events.objects.filter(category=category).order_by("-created_at")
    )

    paginator = Paginator(events, 8)
    events_page = paginator.get_page(page)

    context = {
        "events": events_page,
        "active_category": category,
    }

    if request.htmx:
        return render(request, "events/partials/event_list.html", context)

    return render(request, "events/home.html", context)


def event_detail(request):
    return render(request, "events/event_detail.html")
