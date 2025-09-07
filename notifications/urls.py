from django.urls import path
from . import views

urlpatterns = [
    path("notif/partials", views.notifications_partial, name="notifications_partial"),
    path("notifications", views.notifications_list, name="notifications_list"),
    path("notification/mark-as-read/<str:notif_id>", views.mark_notification_read, name="mark_notification_read")
]
