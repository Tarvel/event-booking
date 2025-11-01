from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm, UpdateProfileForm
from booking.models import Registration
from django.contrib import messages
from django.utils import timezone

from django.core.paginator import Paginator
from datetime import datetime
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import uuid
from events.models import Events
from django.contrib.auth import get_user_model

User = get_user_model()


def registerPage(request):
    username = str(uuid.uuid4())
    form = RegisterForm()
    method = request.method
    if method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            login(request, user)

            return redirect("home")
        else:
            form = RegisterForm()

    context = {
        "username": username,
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def loginPage(request):
    form = LoginForm()
    method = request.method
    if method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                user_obj = User.objects.filter(email=email).first()
            except User.DoesNotExist:
                messages.error(request, "No account found with that email.")
                return redirect("login")

            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                messages.info(request, f"You are now signed in as {user_obj.email}")
                next_url = request.POST.get("next") or "home"
                return redirect(next_url)
            else:
                messages.error(request, "Email or Password incorrect")
                return redirect("login")

        else:
            form = LoginForm()

    context = {
        "form": form,
        "next": request.GET.get("next", ""),
    }

    return render(request, "accounts/login.html", context)


@login_required(login_url="login")
def logoutPage(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def profilePage(request):
    user = request.user
    full_name = (
        f"{user.first_name} {user.last_name}"
        if user.first_name != "" or user.last_name != ""
        else None
    )

    todays_date = datetime.now().date()
    todays_time = datetime.now().time()
    registrations = Registration.objects.filter(user=user, status="approved").order_by(
        "-registered_at"
    )

    paginator = Paginator(registrations, 5)
    page = request.GET.get("page", 1)
    reg_obj = paginator.get_page(page)

    context = {
        "user": user,
        "full_name": full_name,
        "registrations": reg_obj,
        "todays_date": todays_date,
        "todays_time": todays_time,
    }

    if request.htmx:
        return render(request, "partials/registrations.html", context)

    return render(request, "accounts/profile.html", context)


@login_required(login_url="login")
def update_profile(request):
    user = request.user

    if request.method == "POST":
        form = UpdateProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()

            messages.success(request, "Profile updated successfully")

            next_url = request.POST.get("next")

            if next_url != "None":
                return redirect(next_url)
            else:
                return redirect("profile")

    else:
        form = UpdateProfileForm(instance=user)

    referer_url = request.META.get("HTTP_REFERER")

    context = {
        "form": form,
        "next_url": referer_url,
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required(login_url="login")
def dashboard(request):
    user = request.user if request.user.is_authenticated else None
    if user.is_organizer is False:
        messages.error(request, "UNAUTHORIZED")
        return redirect("home")
    events = Events.objects.filter(organizer=user)
    registrations = Registration.objects.filter(status="approved").order_by(
        "-registered_at"
    )
    published = Events.objects.filter(organizer=user, is_published=True).count()
    draft = Events.objects.filter(organizer=user, is_published=False).count()

    total_ticket = 0
    total_revenue = 0
    for event in events:
        total_ticket = int(total_ticket) + event.ticket_bought
        total_revenue = total_revenue + event.revenue

    context = {
        "events": events.order_by("-created_at")[0:4],
        "published": published,
        "draft": draft,
        "total_ticket": total_ticket,
        "total_revenue": total_revenue,
        "registrations": registrations,
        "user": user,
    }
    return render(request, "accounts/dashboard.html", context)


def password_change_done(request):
    messages.success(request, "password changed sucessfully")
    return redirect("profile")
