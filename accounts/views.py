from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm, UpdateProfileForm
from booking.models import Registration
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import uuid
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

            print(user.username, user.is_organizer)

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
                print(next_url)
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

    todays_date = timezone.now().date()
    todays_time = timezone.now().time()
    registrations = Registration.objects.filter(user=user, status="approved").order_by(
        "-registered_at"
    )

    context = {
        "user": user,
        "full_name": full_name,
        "registrations": registrations,
        "todays_date": todays_date,
        "todays_time": todays_time,
    }
    return render(request, "accounts/profile.html", context)


@login_required(login_url="login")
def update_profile(request):
    user = request.user
    form = UpdateProfileForm(instance=user)
    method = request.method
    if method == "POST":
        form = UpdateProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.email = form.cleaned_data["username"]
            user = form.save(commit=False)
            user.username = user.email
            user.save()

            messages.info(request, "Profile updated successfully")
            return redirect("profile")
        else:
            form = UpdateProfileForm()

    context = {"form": form}
    return render(request, "accounts/edit_profile.html", context)
