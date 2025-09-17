from django.contrib.auth import views as auth_views
from .forms import TailwindPasswordChangeForm
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutPage, name="logout"),
    path("profile/", views.profilePage, name="profile"),
    path("profile/update", views.update_profile, name="update_profile"),
    
    path("password/change/", auth_views.PasswordChangeView.as_view(form_class=TailwindPasswordChangeForm), name="password_change"),
    path("password/change/done", views.password_change_done, name="password_change_done"),
    
    path("dashboard/", views.dashboard, name="dashboard")
]
