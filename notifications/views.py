from django.shortcuts import render
from .models import Notification


def notifications_partial(request):
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    unread = Notification.objects.filter(is_read=False)
    context = {
        "notifications": notifications,
        "unread": unread,
    }

    return render(request, "partials/_notifications.html", context)


def notifications_list(request):
    return render(request, "notifications/notifications.html")

def mark_notification_read(request, notif_id):
    mark = Notification.objects.get(id=notif_id)
    mark.is_read = True
    mark.save(update_fields=["is_read"])
    mark.refresh_from_db()
    pass
