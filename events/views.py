from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import EventForm
from datetime import datetime
from .models import Events
from booking.models import Registration, Ticket
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage

User = get_user_model()

from django.template.loader import get_template
import qrcode
from io import BytesIO
import base64
from xhtml2pdf import pisa


def home(request):
    method = request.method
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
    page = request.GET.get("page", 1)
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
    if user.is_authenticated:
        org_eve = Events.objects.filter(slug=slug, is_published=False).first()
        if org_eve and org_eve.organizer is not user:
            messages.error(request, "UNAUTHORIZED")
            return redirect("home")
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
def validateTicket(request, slug):
    user = request.user
    eventtos = Events.objects.filter(organizer=user, slug=slug)
    eventt = eventtos.first()
    print(eventt)
    if not user.is_organizer or not eventtos.exists():
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    if request.method == "POST":
        qr_data = request.POST.get("qr_data")
        ticket = Ticket.objects.filter(unique_code=qr_data, registration__event__slug=slug)
        actual_ticket = ticket.first()
        event = actual_ticket.registration.event
        if ticket:

            if not actual_ticket.is_used:
                # update ticket usage status and time
                actual_ticket.is_used = True
                actual_ticket.scanned_date = timezone.now()

                # updated used ticekts
                event.used_ticket += 1

                # save event and ticket
                event.save(update_fields=["available_ticket"])
                actual_ticket.save(update_fields=["is_used", "scanned_date"])

                return redirect("valid_ticket", actual_ticket.registration.event.slug)

            if actual_ticket.is_used:
                return redirect("used_ticket", actual_ticket.registration.event.slug)
        else:
            return redirect("invalid_ticket")

    return render(request, "events/validate_ticket.html", {"event": eventt})


@login_required(login_url="login")
def validTik(request, slug):
    if not request.user.is_organizer:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    try:
        reg = Registration.objects.filter(event__slug=slug)
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


@login_required(login_url="login")
def create_event(request):
    user = request.user
    if user.is_organizer is False:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")

    form = EventForm()

    if request.method == "POST":
        action = request.POST.get("action")
        form = EventForm(request.POST)
        if form.is_valid():
            print(form.data)
            cd = form.cleaned_data

            event = Events.objects.create(
                organizer=user,
                title=cd["title"],
                description=cd["description"],
                category=cd["category"],
                image=cd["image"],
                start_date=cd["start_date"],
                start_time=cd["start_time"],
                end_date=cd["end_date"],
                end_time=cd["end_time"],
                venue=cd["venue"],
                latitude=cd["latitude"],
                longitude=cd["longitude"],
                ticket_price=cd["ticket_price"],
                max_capacity=cd["max_capacity"],
            )

            if action == "publish":
                event.published_at = timezone.now()
                event.is_published = True
                messages.success(request, "Event has been created and published")
            else:
                event.is_published = False
                messages.success(request, "Event has been created and saved to drafts")

            event.save()

            return redirect("my_events")

        else:
            form = EventForm()

    return render(request, "events/create_event.html", {"form": form})


@login_required(login_url="login")
def edit_event(request, slug):
    page = "edit"
    user = request.user if request.user.is_authenticated else None
    if user.is_organizer is False:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    org_eve = Events.objects.filter(slug=slug).first()
    if org_eve.organizer != user:
        print(f"{user} and {org_eve.organizer}")
        messages.error(request, "UNAUTHORIZED TEST")
        return redirect("home")

    event = Events.objects.filter(organizer=user, slug=slug).first()
    actual_event = Events.objects.get(slug=slug)

    form = EventForm(instance=event)
    print(event.category)

    if request.method == "POST":
        action = request.POST.get("action")
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            if form.has_changed():
                cd = form.cleaned_data
                actual_event.organizer = user
                actual_event.title = cd["title"]
                actual_event.description = cd["description"]
                actual_event.category = cd["category"]
                actual_event.image = cd["image"]
                actual_event.start_date = cd["start_date"]
                actual_event.start_time = cd["start_time"]
                actual_event.end_date = cd["end_date"]
                actual_event.end_time = cd["end_time"]
                actual_event.venue = cd["venue"]
                actual_event.latitude = cd["latitude"]
                actual_event.longitude = cd["longitude"]
                actual_event.ticket_price = cd["ticket_price"]
                actual_event.max_capacity = cd["max_capacity"]

                actual_event.save()
                messages.success(request, "Event has been updated")

            else:
                messages.info(request, "No changes made")

            return redirect("event_detail", event.slug)

        else:
            form = EventForm(instance=event)
    return render(request, "events/create_event.html", {"form": form, "page": page})


@login_required(login_url="login")
def publish_event(request, slug):
    event = Events.objects.get(slug=slug)
    event.is_published = True
    event.published_at = timezone.now()
    event.save(update_fields=["is_published", "published_at"])
    messages.success(request, "Event has been published")
    return redirect("event_detail", event.slug)


@login_required(login_url="login")
def my_events(request):
    user = request.user if request.user.is_authenticated else None
    if user.is_organizer is False:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    active_status = request.GET.get("status")
    if active_status == "published":
        events = Events.objects.filter(organizer=user, is_published=True)
    elif active_status == "drafts":
        events = Events.objects.filter(organizer=user, is_published=False)
    else:
        events = Events.objects.filter(organizer=user, is_published=True)
    events = events.order_by("-created_at")
    return render(
        request,
        "events/my_events.html",
        {"events": events, "active_status": active_status},
    )


@login_required(login_url="login")
def checkPage(request):
    user = request.user
    if user.is_organizer is False:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")

    events = Events.objects.filter(organizer=user).order_by(
        "-start_date", "-start_time"
    )

    for e in events:
        e.percentage = (e.used_ticket / e.max_capacity) * 100

    context = {
        "events": events,
    }
    return render(request, "events/check_in.html", context)


# ths parts for nomatim autocomplete for venue in create event
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
    headers = {"User-Agent": "EventBooking"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return JsonResponse(data, safe=False)


def dt(slug, user):
    reg = Registration.objects.filter(event__slug=slug).first()
    tic = Ticket.objects.get(registration=reg)
    ticket_code = tic.unique_code

    # Generate QR code
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

    pdf_buffer = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer)

    # Create the email
    email = EmailMessage(
        "Your Event Ticket",
        "Please find attached your ticket.",
        "ayodeji.tbbtnd@gmail.com",
        [user.email],
    )

    # Attach the PDF
    filename = f"{reg.event.title.title()}_Ticket_For_{user.email}.pdf"
    email.attach(filename, pdf_buffer.getvalue(), "application/pdf")

    email.send(fail_silently=False)
