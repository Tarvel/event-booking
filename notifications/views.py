from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Notification
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


@login_required(login_url="login")
def notifications_partial(request):
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )[0:3]
    unread = Notification.objects.filter(is_read=False)
    context = {
        "notifications": notifications,
        "unread": unread,
    }

    return render(request, "partials/_notifications.html", context)


@login_required(login_url="login")
def notifications_list(request):
    status = request.GET.get("status", "all")
    print(status)
    notifications = (
        Notification.objects.filter(user=request.user, is_read=False).order_by(
            "-created_at"
        )
        if status == "unread"
        else Notification.objects.filter(user=request.user).order_by("-created_at")
    )
    paginator = Paginator(notifications, 5)
    page = request.GET.get("page", 1)
    notif_obj = paginator.get_page(page)

    context = {
        "notifications": notif_obj,
        "status": status,
    }
    if request.htmx:
        return render(request, "notifications/partials/notification_htmx.html", context)
    return render(request, "notifications/notifications.html", context)


@login_required(login_url="login")
def mark_notification_read(request, notif_id):
    mark = Notification.objects.get(id=notif_id)
    mark.is_read = True
    mark.save(update_fields=["is_read"])
    mark.refresh_from_db()
    return HttpResponse(status=200)


@login_required(login_url="login")
def mark_all_read(request):
    notifications = Notification.objects.filter(is_read=False)
    for notification in notifications:
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return redirect('notifications_list')
