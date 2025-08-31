from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
import uuid
from datetime import datetime
from .models import Events
from django.contrib.auth import get_user_model

User = get_user_model()


def home(request):
    method = request.method
    page = request.GET.get("page", 1)

    category = request.COOKIES.get("tempCategory") or "all"
    date = request.COOKIES.get("tempDate") or "all"

    filters = Q()
    compared_date = datetime.now().date()

    if category and category != "all":
        filters &= Q(category=category)

    if date == "today":
        filters &= Q(start_date=compared_date)

    elif date == "week":
        filters &= Q(start_date__week=(compared_date.isocalendar()[1]))
        filters &= Q(start_date__year=compared_date.year)

    elif date == "month":
        filters &= Q(start_date__month=compared_date.month)

    events = (
        Events.objects.all().order_by("-created_at")
        if category == "all" and date == "all"
        else Events.objects.filter(filters).order_by("-created_at")
    )
    print(
        f"this is {date}\n compared week {compared_date.isocalendar()[1]}\n today {compared_date}"
    )
    print("compared_date:", compared_date)
    print("filters:", filters)
    print(
        "events in DB:", list(Events.objects.values_list("start_date__week", flat=True))
    )

    paginator = Paginator(events, 8)
    events_page = paginator.get_page(page)

    context = {
        "events": events_page,
        "active_category": category,
        "active_date": date,
    }

    if request.htmx:
        return render(request, "events/partials/event_list.html", context)
    return render(request, "events/home.html", context)


def event_detail(request, slug):
    event = Events.objects.get(slug=slug)
    if request.htmx:
        return render(request, "events/modal/event_detail_modal.html")
    context = {
        "event": event,
    }
    return render(request, "events/event_detail.html", context)
