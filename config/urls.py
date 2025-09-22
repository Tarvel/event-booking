from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("events.urls")),
    path("", include("payment.urls")),
    path("", include("notifications.urls")),
]


if settings.DEBUG is True:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
