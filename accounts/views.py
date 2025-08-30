from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


def registerPage(request):
    username = uuid.uuid4()
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
                return redirect(next_url)
            else:
                messages.error(request, "Email or Password incorrect")
                return redirect("login")

        else:
            form = LoginForm()

    context = {"form": form}

    return render(request, "accounts/login.html", context)


def logoutPage(request):
    logout(request)
    return redirect("home")