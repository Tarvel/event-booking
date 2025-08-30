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

    category = request.POST.get("category", "all")

    s_date = request.COOKIES.get("tempWord") or "all"

    filters = Q()
    compared_date = datetime.now()

    if category:
        filters &= Q(category=category)

    if s_date == "today":
        filters &= Q(start_date=compared_date)

    elif s_date == "week":
        filters &= Q(start_date__week=compared_date.isocalendar()[1])
        filters &= Q(start_date__year=compared_date.year)

    elif s_date == "month":
        filters &= Q(start_date__month=compared_date.month)

    events = (
        Events.objects.all()
        if category == "all" and s_date == "all"
        else Events.objects.filter(filters)
    )
    print(f"this is {s_date}")
    paginator = Paginator(events, 8)
    events_page = paginator.get_page(page)

    context = {
        "events": events_page,
        "active_category": category,
        "active_date": s_date,
    }

    if request.htmx:
        return render(request, "events/partials/event_list.html", context)
    return render(request, "events/home.html", context)


def event_detail(request):
    return render(request, "events/event_detail.html")
