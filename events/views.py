from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import uuid
from datetime import datetime
from .models import Events
from booking.models import Registration, Ticket
from django.contrib.auth import get_user_model

User = get_user_model()

from django.template.loader import get_template
import qrcode
from io import BytesIO
import base64
from xhtml2pdf import pisa


def home(request):
    method = request.method
    page = request.GET.get("page", 1)

    category = request.COOKIES.get("tempCategory") or "all"
    date = request.COOKIES.get("tempDate") or "all"

    filters = Q()
    compared_date = datetime.now().date()

    filters &= Q(start_date__gte=compared_date)

    if category and category != "all":
        filters &= Q(category=category)

    if date == "today":
        filters &= Q(start_date=compared_date)

    elif date == "week":
        filters &= Q(start_date__week=(compared_date.isocalendar()[1]))
        filters &= Q(start_date__year=compared_date.year)

    elif date == "month":
        filters &= Q(start_date__month=compared_date.month)

    events = Events.objects.filter(filters).order_by("-created_at")

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
    user = request.user
    event = Events.objects.get(slug=slug)
    if user.is_authenticated:
        registration = Registration.objects.filter(
            user=user, event=event, status="approved"
        )
    else:
        registration = None

    if request.htmx:
        return render(request, "events/modal/event_detail_modal.html")
    context = {
        "event": event,
        "registration": registration,
    }
    return render(request, "events/event_detail.html", context)


def download_ticket(request, slug):
    reg = Registration.objects.filter(event__slug=slug).first()
    tic = Ticket.objects.get(registration=reg)
    ticket_code = tic.unique_code
    user = request.user

    img = qrcode.make(ticket_code)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    template = get_template("ticket.html")
    html = template.render(
        {
            "user": user,
            "qr_image": img_base64,
            "reg": reg,
        }
    )

    pisa.CreatePDF(html, dest=buffer)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    buffer.close()

    response["Content-Disposition"] = (
        f'attachment; filename="{reg.event.title.title()}_Ticket_For_{user.email}.pdf"'
    )
    return response


@login_required(login_url="login")
def validateTicket(request):
    if not request.user.is_organizer:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    if request.method == "POST":
        qr_data = request.POST.get("qr_data")
        ticket = Ticket.objects.filter(
            registration__user=request.user, unique_code=qr_data
        )
        actual_ticket = ticket.first()
        if ticket:

            if not actual_ticket.is_used:
                actual_ticket.is_used = True
                actual_ticket.scanned_date = timezone.now()
                actual_ticket.save(update_fields=["is_used", "scanned_date"])
                return redirect("valid_ticket", actual_ticket.registration.event.slug)

            if actual_ticket.is_used:
                return redirect("used_ticket", actual_ticket.registration.event.slug)
        else:
            return redirect("invalid_ticket")

    return render(request, "events/validate_ticket.html")


@login_required(login_url="login")
def validTik(request, slug):
    if not request.user.is_organizer:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    try:
        reg = Registration.objects.filter(user=request.user, event__slug=slug)
    except Registration.DoesNotExist:
        messages.error(request, "Invalid")
        return redirect("home")
    return render(request, "events/valid_ticket.html", {"reg": reg.first()})


@login_required(login_url="login")
def invalidTik(request):
    return render(request, "events/invalid_ticket.html")


@login_required(login_url="login")
def usedTik(request, slug):
    if not request.user.is_organizer:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    try:
        reg = Registration.objects.filter(user=request.user, event__slug=slug)
    except Registration.DoesNotExist:
        messages.error(request, "Invalid")
        return redirect("home")
    return render(request, "events/used_ticket.html", {"reg": reg.first()})


# scan_link = "TEST"
# img = qrcode.make(scan_link)

# # Convert to BytesIO buffer
# buffer = BytesIO()
# img.save(buffer, format="PNG")
# img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
# buffer.close()
# context = {
#     "qr_image": img_base64,
# }

# nomatim autocomplete for venue in create event
import requests
from django.http import JsonResponse

def place_autocomplete(request):
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse([], safe=False)

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
    }
    headers = {"User-Agent": "EventBooking"}  # required by Nominatim

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return JsonResponse(data, safe=False)
