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

from django.template.loader import get_template
from weasyprint import HTML
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


def download_ticket(request):

    order = "TEST001"
    user = request.user
    scan_link = "TEST"
    img = qrcode.make(scan_link)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    template = get_template("ticket.html")
    html = template.render(
        {
            "user": user,
            "qr_image": img_base64,
        }
    )

    pisa.CreatePDF(html, dest=buffer)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    buffer.close()

    response["Content-Disposition"] = (
        f'attachment; filename="{user.first_name}_ticket.pdf"'
    )
    return response


scan_link = "TEST"
img = qrcode.make(scan_link)

# Convert to BytesIO buffer
buffer = BytesIO()
img.save(buffer, format="PNG")
img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
buffer.close()
context = {
    "qr_image": img_base64,
}
