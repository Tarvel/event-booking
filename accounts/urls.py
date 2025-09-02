from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutPage, name="logout"),
    path("profile/", views.profilePage, name="profile"),
    path("profile/update", views.update_profile, name="update_profile"),
]
